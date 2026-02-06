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
        Classify a document based on its extracted text content.
        
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
            # Build classification prompt
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
                        "temperature": 0.1,
                        "num_predict": 500
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

    def _build_classification_prompt(self, text: str) -> str:
        """Build the classification prompt for Ollama"""
        # Use more text for better extraction (first 2500 characters)
        text_sample = text[:2500] if len(text) > 2500 else text
        
        prompt = f"""Extrahiere Rechnungsdaten aus diesem Dokument. Antworte NUR mit JSON, keine zusätzlichen Texte.

DOKUMENT:
{text_sample}

AUFGABE:
1. Prüfe ob dies eine Rechnung ist
2. Typ: "incoming" wenn ich bezahlen muss, "outgoing" wenn ich der Absender bin
3. Extrahiere: Rechnungsnummer, Datum, Betrag (als Zahl!), Lieferant/Kunde

JSON ANTWORT:
{{
  "is_invoice": true,
  "invoice_type": "incoming",
  "confidence": 0.9,
  "reasoning": "Enthält Rechnungsnummer und Betrag",
  "invoice_number": "RE-2024-001",
  "invoice_date": "2024-01-26",
  "due_date": "2024-02-26",
  "total_amount": 1234.56,
  "net_amount": 1000.00,
  "tax_amount": 234.56,
  "currency": "EUR",
  "vendor_name": "Musterfirma GmbH",
  "vendor_address": "Musterstraße 1, 12345 Stadt",
  "customer_name": "Kunde XY"
}}

WICHTIG:
- total_amount, net_amount, tax_amount sind ZAHLEN (nicht Strings!)
- Datum Format: YYYY-MM-DD
- Falls Feld nicht gefunden: null (nicht "null" als String!)"""

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
