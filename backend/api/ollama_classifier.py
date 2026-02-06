"""
Ollama AI classifier for document type detection
"""
import os
import json
import logging
import requests
from typing import Dict, Optional

logger = logging.getLogger(__name__)

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://host.docker.internal:11434")


class OllamaClassifier:
    """Classify documents using local Ollama AI"""

    def __init__(self):
        self.api_url = OLLAMA_API_URL
        # Read model dynamically instead of at module load
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")

    def classify_document(self, markdown_text: str) -> Dict:
        """
        STEP 1: Quick classification only - is this an invoice?
        
        Args:
            markdown_text: OCR extracted text in markdown format
            
        Returns:
            Dict containing:
                - is_invoice (bool): Whether the document is an invoice
                - invoice_type (str): 'incoming', 'outgoing', or None
                - confidence (float): Confidence score 0-1
                - reasoning (str): AI explanation
        """
        try:
            # Build simple classification prompt (no data extraction)
            prompt = self._build_classification_prompt(markdown_text)
            
            # Call Ollama API
            response = requests.post(
                f"{self.api_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0,
                        "num_predict": 150
                    }
                },
                timeout=300
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return self._default_classification()
            
            # Parse response
            result = response.json()
            ai_response = result.get("response", "{}")
            
            # Parse JSON from AI response
            try:
                classification = json.loads(ai_response)
                return {
                    "is_invoice": classification.get("is_invoice", False),
                    "invoice_type": classification.get("invoice_type"),
                    "confidence": classification.get("confidence", 0.0),
                    "reasoning": classification.get("reasoning", "")
                }
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI response as JSON: {ai_response}")
                return self._default_classification()
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API connection error: {e}")
            return self._default_classification()
        except Exception as e:
            logger.error(f"Unexpected error in classify_document: {e}")
            return self._default_classification()

    def extract_invoice_data(self, markdown_text: str, invoice_type: str) -> Dict:
        """
        STEP 2: Extract invoice data (called only if is_invoice=True)
        
        Args:
            markdown_text: OCR extracted text
            invoice_type: 'incoming' or 'outgoing'
            
        Returns:
            Dict with extracted invoice fields
        """
        try:
            prompt = self._build_extraction_prompt(markdown_text, invoice_type)
            
            print(f"[OLLAMA] Calling API for extraction with model {self.model}")
            
            # Call Ollama API for data extraction
            response = requests.post(
                f"{self.api_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0,
                        "num_predict": 350
                    }
                },
                timeout=360
            )
            
            print(f"[OLLAMA] Extraction response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"[OLLAMA] API error: {response.status_code} - {response.text[:200]}")
                return {}
            
            result = response.json()
            ai_response = result.get("response", "{}")
            
            print(f"[OLLAMA] Raw AI response (first 300 chars): {ai_response[:300]}")
            
            try:
                extracted = json.loads(ai_response)
                print(f"[OLLAMA] Successfully parsed JSON, keys: {list(extracted.keys())}")
                return extracted
            except json.JSONDecodeError as e:
                print(f"[OLLAMA] JSON parse error: {e}")
                print(f"[OLLAMA] Full response: {ai_response}")
                return {}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama extraction connection error: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error in extract_invoice_data: {e}")
            return {}

    def _build_classification_prompt(self, text: str) -> str:
        """Build SIMPLE classification prompt (no extraction)"""
        text_sample = text[:1500] if len(text) > 1500 else text
        
        prompt = f"""AUFGABE: Klassifiziere diese Rechnung.

TEXT:
{text_sample}

REGELN:
1. is_invoice = true wenn Text "Rechnung", "Invoice" oder "RE-" enthält
2. invoice_type:
   - WENN Text "An IMO" oder "An CompuGroup" ODER "Empfänger:" enthält:
     → invoice_type = "outgoing" (Dr. Micka schreibt AN Kunden = Einnahme)
   - WENN Text "Von IMO" oder "Absender: CompuGroup" enthält:
     → invoice_type = "incoming" (Dr. Micka erhält VON Lieferant = Ausgabe)
   - EINFACHE REGEL: Steht "Dr. med. Björn Micka" VOR dem Firmennamen = outgoing

BEISPIEL OUTGOING:
"Dr. med. Björn Micka\nAn IMO GmbH" → outgoing (Micka schreibt AN IMO)

BEISPIEL INCOMING:
"CompuGroup Medical\nAn Dr. med. Björn Micka" → incoming (CompuGroup schreibt AN Micka)

JSON: {{"is_invoice": true, "invoice_type": "outgoing", "confidence": 0.95, "reasoning": "Dr. Micka schreibt AN IMO"}}"""
        return prompt

    def _build_extraction_prompt(self, text: str, invoice_type: str) -> str:
        """Build focused extraction prompt"""
        text_sample = text[:2000] if len(text) > 2000 else text
        
        if invoice_type == "outgoing":
            vendor_hint = "Dr. med. Björn Micka (DER ABSENDER)"
            customer_hint = "SUCHE Empfänger nach 'An' (z.B. 'An IMO GmbH')"
        else:
            vendor_hint = "SUCHE Absender/Lieferant (Firma die Rechnung schickt)"
            customer_hint = "Dr. med. Björn Micka (DER EMPFÄNGER)"
        
        prompt = f"""Extrahiere ALLE Daten aus dieser {invoice_type.upper()} Rechnung.

TEXT:
{text_sample}

WICHTIG - {invoice_type.upper()} Rechnung bedeutet:
- vendor_name: {vendor_hint}
- customer_name: {customer_hint}

EXTRAHIERE:
- invoice_number: Rechnungsnummer (bei "Rechnung", z.B. "2026-F00016-R001")
- invoice_date: Datum (Format YYYY-MM-DD, z.B. "2026-01-13")
- due_date: Fälligkeitsdatum
- total_amount: Endbetrag als ZAHL (z.B. 13199.06)
- net_amount: Nettobetrag
- tax_amount: MwSt-Betrag
- currency: "EUR"
- vendor_name: {vendor_hint}
- vendor_address: Vollständige Adresse des Lieferanten
- customer_name: {customer_hint}
- customer_address: Vollständige Adresse des Kunden

JSON (null wenn nicht gefunden):
{{"invoice_number": "2026-F00016-R001", "invoice_date": "2026-01-13", "due_date": null, "total_amount": 13199.06, "net_amount": 11162.06, "tax_amount": 2037.00, "currency": "EUR", "vendor_name": "Dr. med. Björn Micka", "vendor_address": "Christoph-Dassler-Str. 22, 91074 Herzogenaurach", "customer_name": "IMO GmbH & Co. KG", "customer_address": "Imostraße 1, 91350 Gremsdorf"}}"""
        return prompt

    def _default_classification(self) -> Dict:
        """Return default classification when AI fails"""
        return {
            "is_invoice": False,
            "invoice_type": None,
            "confidence": 0.0,
            "reasoning": "AI classification failed or unavailable"
        }

    def health_check(self) -> bool:
        """Check if Ollama API is reachable"""
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
