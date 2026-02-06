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
        # Truncate text if too long (keep first 2000 characters)
        text_sample = text[:2000] if len(text) > 2000 else text
        
        prompt = f"""Extrahiere Rechnungsdaten aus diesem Dokument. Antworte NUR mit JSON.

Text:
{text_sample}

JSON Format:
{{
  "is_invoice": true/false,
  "invoice_type": "incoming"|"outgoing"|null,
  "confidence": 0.0-1.0,
  "reasoning": "kurz",
  "invoice_number": "RE-123" oder null,
  "invoice_date": "2024-01-26" oder null,
  "due_date": "2024-02-26" oder null,
  "total_amount": 123.45 oder null,
  "net_amount": 100.00 oder null,
  "tax_amount": 23.45 oder null,
  "currency": "EUR" oder null,
  "vendor_name": "Firma" oder null,
  "vendor_address": "Adresse" oder null,
  "customer_name": "Kunde" oder null
}}

Regeln:
- incoming = ich muss bezahlen
- outgoing = ich habe geschrieben
- Alle Beträge als Dezimalzahl
- Datum im Format YYYY-MM-DD"""

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
