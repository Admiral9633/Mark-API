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
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


class OllamaClassifier:
    """Classify documents using local Ollama AI"""

    def __init__(self):
        self.api_url = OLLAMA_API_URL
        self.model = OLLAMA_MODEL

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
            
            if response.status_code != 200:
                logger.error(f"Ollama extraction API error: {response.status_code}")
                return {}
            
            result = response.json()
            ai_response = result.get("response", "{}")
            
            try:
                extracted = json.loads(ai_response)
                logger.info(f"Extracted invoice data: {extracted}")
                return extracted
            except json.JSONDecodeError:
                logger.error(f"Failed to parse extraction response: {ai_response}")
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
        
        prompt = f"""Ist dies eine Rechnung?

Text:
{text_sample}

Antwort als JSON:
- is_invoice: true/false (suche "Rechnung", "Invoice", "RE-")
- invoice_type: "outgoing" wenn von "Dr. med. Björn Micka", sonst "incoming"
- confidence: 0.0-1.0
- reasoning: kurze Begründung

Beispiel: {{"is_invoice": true, "invoice_type": "outgoing", "confidence": 0.9, "reasoning": "Rechnung gefunden"}}"""
        return prompt

    def _build_extraction_prompt(self, text: str, invoice_type: str) -> str:
        """Build focused extraction prompt"""
        text_sample = text[:2000] if len(text) > 2000 else text
        
        if invoice_type == "outgoing":
            vendor_hint = "Dr. med. Björn Micka"
            customer_hint = "Empfänger im Dokument"
        else:
            vendor_hint = "Absender/Lieferant im Dokument"
            customer_hint = "Dr. med. Björn Micka"
        
        prompt = f"""Extrahiere alle Daten aus dieser Rechnung. Sei präzise.

DOKUMENT:
{text_sample}

EXTRAHIERE:
- invoice_number: Rechnungsnummer (z.B. "2026-F00023-R001")
- invoice_date: Rechnungsdatum (Format: YYYY-MM-DD)
- due_date: Fälligkeitsdatum (Format: YYYY-MM-DD)
- total_amount: Gesamtbetrag (Zahl, z.B. 150.00)
- net_amount: Nettobetrag
- tax_amount: MwSt-Betrag
- currency: Währung (meist "EUR")
- vendor_name: {vendor_hint}
- vendor_address: Vollständige Adresse des Absenders
- customer_name: {customer_hint}

JSON Format (nutze null wenn nicht gefunden):
{{
  "invoice_number": "2026-F00023-R001",
  "invoice_date": "2026-01-21",
  "due_date": null,
  "total_amount": 150.00,
  "net_amount": null,
  "tax_amount": null,
  "currency": "EUR",
  "vendor_name": "Dr. med. Björn Micka",
  "vendor_address": "Musterstr. 1, 12345 Stadt",
  "customer_name": "Max Mustermann"
}}"""
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
