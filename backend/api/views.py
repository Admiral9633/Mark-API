import os
import requests
from pathlib import Path
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from .models import Document
from .serializers import DocumentSerializer, DocumentUploadSerializer
from .ollama_classifier import OllamaClassifier
from .lexoffice_client import LexofficeClient

# Marker-API URL aus Environment
MARKER_API_URL = os.getenv('MARKER_API_URL', 'http://localhost:8001')
MARKER_AVAILABLE = True  # Wird über Docker-Service bereitgestellt

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """
        Bestehendes Dokument neu verarbeiten
        """
        document = self.get_object()
        document.status = 'processing'
        document.error_message = None
        document.save()

        return self._process_document(document)

    @action(detail=False, methods=['post'])
    def convert(self, request):
        """
        PDF hochladen und mit Marker-PDF verarbeiten
        """
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pdf_file = serializer.validated_data['pdf_file']

        # Dokument erstellen
        document = Document.objects.create(
            original_filename=pdf_file.name,
            pdf_file=pdf_file,
            status='processing'
        )

        return self._process_document(document)

    def _process_document(self, document):
        """
        Dokument mit Marker-API verarbeiten (externer Service)
        """
        if not MARKER_AVAILABLE:
            # Fallback: Upload ohne OCR
            document.status = 'completed'
            document.marker_markdown = "# PDF Upload erfolgreich!\n\nMarker-OCR nicht verfügbar."
            document.save()

            return Response(
                DocumentSerializer(document).data,
                status=status.HTTP_200_OK
            )

        try:
            # PDF-Pfad
            pdf_path = document.pdf_file.path
            print(f"[OCR] Sende PDF an Marker-API: {pdf_path}")

            # PDF an Marker-API senden
            with open(pdf_path, 'rb') as pdf_file:
                files = {'pdf': pdf_file}
                response = requests.post(
                    f"{MARKER_API_URL}/convert",
                    files=files,
                    timeout=600  # 10 Minuten Timeout für große PDFs
                )

            if response.status_code == 200:
                result = response.json()
                print(f"[OCR] Marker-API erfolgreich, Markdown Length: {len(result.get('markdown', ''))}")

                # Ergebnisse speichern
                document.marker_markdown = result.get('markdown', '')
                document.marker_json = result.get('metadata', {})
                document.status = 'completed'
                document.save()
                print(f"[OCR] Dokument {document.id} erfolgreich verarbeitet")

                # AI Classification mit Ollama (2-Step Process)
                print(f"[AI] Starte Klassifizierung für Dokument {document.id}")
                try:
                    classifier = OllamaClassifier()
                    
                    # STEP 1: Classify document (fast, ~1-2 minutes)
                    classification = classifier.classify_document(document.marker_markdown)
                    
                    # Speichere Basis-Klassifizierung
                    document.ai_classification = classification
                    document.is_invoice = classification.get('is_invoice', False)
                    document.invoice_type = classification.get('invoice_type')
                    document.save()
                    
                    print(f"[AI] Klassifizierung: is_invoice={document.is_invoice}, type={document.invoice_type}")
                    
                    # STEP 2: Extract invoice data only if is_invoice=True (focused, ~2-3 minutes)
                    if document.is_invoice and document.invoice_type:
                        print(f"[AI] Starte Datenextraktion für {document.invoice_type} Rechnung")
                        extracted_data = classifier.extract_invoice_data(
                            document.marker_markdown,
                            document.invoice_type
                        )
                        
                        if extracted_data:
                            # Speichere extrahierte Daten
                            document.invoice_number = extracted_data.get('invoice_number')
                            document.invoice_date = extracted_data.get('invoice_date')
                            document.due_date = extracted_data.get('due_date')
                            document.total_amount = extracted_data.get('total_amount')
                            document.net_amount = extracted_data.get('net_amount')
                            document.tax_amount = extracted_data.get('tax_amount')
                            document.currency = extracted_data.get('currency') or 'EUR'
                            document.vendor_name = extracted_data.get('vendor_name')
                            document.vendor_address = extracted_data.get('vendor_address')
                            document.customer_name = extracted_data.get('customer_name')
                            
                            # Update ai_classification mit extrahierten Daten
                            document.ai_classification.update(extracted_data)
                            
                            document.save()
                            print(f"[AI] Extraktion erfolgreich: RE-Nr={document.invoice_number}, Betrag={document.total_amount}, Lieferant={document.vendor_name}")
                        else:
                            print(f"[AI] Extraktion fehlgeschlagen oder leer")
                    
                    # Wenn Rechnung erkannt wurde, zu Lexoffice hochladen
                    if document.is_invoice:
                        print(f"[LEXOFFICE] Rechnung erkannt, starte Upload")
                        try:
                            lexoffice_client = LexofficeClient()
                            
                            # Nur invoice_data übergeben, wenn mindestens einige Felder extrahiert wurden
                            invoice_data = None
                            if document.invoice_number or document.total_amount or document.vendor_name or document.customer_name:
                                invoice_data = {
                                    'invoice_number': document.invoice_number,
                                    'invoice_date': str(document.invoice_date) if document.invoice_date else None,
                                    'due_date': str(document.due_date) if document.due_date else None,
                                    'total_amount': float(document.total_amount) if document.total_amount else None,
                                    'net_amount': float(document.net_amount) if document.net_amount else None,
                                    'tax_amount': float(document.tax_amount) if document.tax_amount else None,
                                    'vendor_name': document.vendor_name,
                                    'customer_name': document.customer_name,
                                }
                                print(f"[LEXOFFICE] Sende mit extrahierten Daten: {invoice_data}")
                            else:
                                print(f"[LEXOFFICE] Keine Daten extrahiert, lade nur PDF hoch")
                            
                            upload_result = lexoffice_client.upload_voucher(
                                document.pdf_file.path,
                                voucher_type='voucher',
                                invoice_data=invoice_data,
                                doc_invoice_type=document.invoice_type
                            )
                            
                            if upload_result.get('success'):
                                document.lexoffice_sent = True
                                document.lexoffice_file_id = upload_result.get('file_id')
                                document.lexoffice_voucher_id = upload_result.get('voucher_id')
                                document.save()
                                print(f"[LEXOFFICE] Upload erfolgreich: file_id={document.lexoffice_file_id}")
                            else:
                                document.lexoffice_error = upload_result.get('error')
                                document.save()
                                print(f"[LEXOFFICE] Upload fehlgeschlagen: {document.lexoffice_error}")
                        except Exception as e:
                            document.lexoffice_error = str(e)
                            document.save()
                            print(f"[LEXOFFICE] Fehler beim Upload: {e}")
                except Exception as e:
                    print(f"[AI] Fehler bei Klassifizierung: {e}")
                    # Continue processing even if AI fails

                return Response(
                    DocumentSerializer(document).data,
                    status=status.HTTP_200_OK
                )
            else:
                raise Exception(f"Marker-API Error: {response.status_code} - {response.text}")

        except requests.exceptions.Timeout:
            error_msg = "Marker-API Timeout nach 10 Minuten"
            print(f"[OCR] {error_msg}")
            document.status = 'error'
            document.error_message = error_msg
            document.save()

            return Response(
                {'error': error_msg},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except requests.exceptions.ConnectionError:
            error_msg = f"Marker-API nicht erreichbar unter {MARKER_API_URL}"
            print(f"[OCR] {error_msg}")
            document.status = 'error'
            document.error_message = error_msg
            document.save()

            return Response(
                {'error': error_msg},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"[OCR] Fehler bei Dokument {document.id}:")
            print(error_details)

            document.status = 'error'
            document.error_message = str(e)
            document.save()

            return Response(
                {'error': f'Verarbeitung fehlgeschlagen: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
