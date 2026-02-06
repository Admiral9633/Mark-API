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

                # AI Classification mit Ollama
                print(f"[AI] Starte Klassifizierung für Dokument {document.id}")
                try:
                    classifier = OllamaClassifier()
                    classification = classifier.classify_document(document.marker_markdown)
                    
                    # Speichere AI Klassifizierung
                    document.ai_classification = classification
                    document.is_invoice = classification.get('is_invoice', False)
                    document.invoice_type = classification.get('invoice_type')
                    document.save()
                    
                    print(f"[AI] Klassifizierung abgeschlossen: is_invoice={document.is_invoice}, type={document.invoice_type}")
                    
                    # Wenn Rechnung erkannt wurde, zu Lexoffice hochladen
                    if document.is_invoice:
                        print(f"[LEXOFFICE] Rechnung erkannt, starte Upload")
                        try:
                            lexoffice_client = LexofficeClient()
                            upload_result = lexoffice_client.upload_voucher(
                                document.pdf_file.path,
                                voucher_type='voucher'
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
