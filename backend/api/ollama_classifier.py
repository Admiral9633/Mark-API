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
                    "format": "json"
                },
                timeout=120
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
        
        prompt = f"""Analysiere das folgende Dokument und klassifiziere es. 
Antworte NUR mit einem JSON-Objekt (keine Erklärungen davor oder danach).

Dokumententext:
{text_sample}

Aufgaben:
1. Ist dies eine Rechnung? (is_invoice: true/false)
2. Wenn ja, ist es eine eingehende Rechnung (die ich bezahlen muss) oder eine ausgehende Rechnung (die ich geschrieben habe)?
   - "incoming": Rechnung von einem Lieferanten/Dienstleister an mich (z.B. Hornbach, Edeka, DATEV)
   - "outgoing": Rechnung die ich an einen Kunden geschrieben habe (enthält meine Firmendaten als Absender)
   - null: Wenn es keine Rechnung ist

3. Confidence (0.0 - 1.0): Wie sicher bist du?

Antworte im folgenden JSON-Format:
{{
  "is_invoice": true/false,
  "invoice_type": "incoming"|"outgoing"|null,
  "confidence": 0.0-1.0,
  "reasoning": "Kurze Begründung"
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
