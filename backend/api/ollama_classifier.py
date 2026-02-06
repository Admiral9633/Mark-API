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
                        "temperature": 0,
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
        # Use more text for better extraction (first 3000 characters)
        text_sample = text[:3000] if len(text) > 3000 else text
        
        prompt = f"""Du bist ein Experte für Rechnungserkennung. Analysiere dieses Dokument und gib ein VOLLSTÄNDIGES JSON zurück.

DOKUMENT:
{text_sample}

DEINE AUFGABEN:
1. Ist dies eine Rechnung? Suche nach "Rechnung", "Invoice", "RE-", Rechnungsnummer
2. invoice_type bestimmen:
   - "outgoing": Absender ist "Dr. med. Björn Micka" → ICH habe die Rechnung geschrieben
   - "incoming": Absender ist eine andere Firma → ICH muss bezahlen
3. EXTRAHIERE alle Daten (auch wenn schwer zu finden):
   - invoice_number: Die Rechnungsnummer (z.B. "2026-F00023-R001")
   - invoice_date: Das Rechnungsdatum im Format YYYY-MM-DD
   - total_amount: Der Gesamtbetrag als ZAHL (z.B. 150.00)
   - vendor_name: Der Name des Absenders
   - customer_name: Der Name des Empfängers

ANTWORTE mit diesem EXAKTEN JSON (ALLE Felder müssen vorhanden sein!):
{{
  "is_invoice": true,
  "invoice_type": "outgoing",
  "confidence": 0.95,
  "reasoning": "Rechnung 2026-F00023-R001 gefunden",
  "invoice_number": "2026-F00023-R001",
  "invoice_date": "2026-01-21",
  "due_date": null,
  "total_amount": 150.00,
  "net_amount": null,
  "tax_amount": null,
  "currency": "EUR",
  "vendor_name": "Dr. med. Björn Micka",
  "vendor_address": null,
  "customer_name": "Erkan Ökcü"
}}

REGELN:
- Beträge als Zahlen (150.00 nicht "150.00")
- Wenn Feld nicht gefunden: null (nicht weglassen!)
- Datum: YYYY-MM-DD Format
- ALLE 14 Felder MÜSSEN im JSON sein"""

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
