"""
Lexoffice API client for uploading vouchers (invoices)
"""
import os
import logging
import requests
from typing import Optional, Dict

logger = logging.getLogger(__name__)

LEXOFFICE_API_KEY = os.getenv("LEXOFFICE_API_KEY")
LEXOFFICE_API_URL = os.getenv("LEXOFFICE_API_URL", "https://api.lexware.io")


class LexofficeClient:
    """Client for Lexoffice API integration"""

    def __init__(self):
        self.api_key = LEXOFFICE_API_KEY
        self.api_url = LEXOFFICE_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

    def upload_voucher(self, pdf_file_path: str, voucher_type: str = "voucher") -> Dict:
        """
        Upload a voucher (invoice) to Lexoffice
        
        Args:
            pdf_file_path: Path to the PDF file
            voucher_type: Type of voucher (default: "voucher" for bookkeeping)
            
        Returns:
            Dict containing:
                - success (bool): Upload successful
                - file_id (str): Lexoffice file ID
                - voucher_id (str): Lexoffice voucher ID
                - error (str): Error message if failed
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "Lexoffice API key not configured"
            }

        try:
            # Prepare multipart upload
            with open(pdf_file_path, 'rb') as pdf_file:
                files = {
                    'file': ('invoice.pdf', pdf_file, 'application/pdf'),
                    'type': (None, voucher_type)
                }
                
                # Upload to Lexoffice
                response = requests.post(
                    f"{self.api_url}/v1/files",
                    headers=self.headers,
                    files=files,
                    timeout=60
                )

            if response.status_code == 202:  # Accepted
                result = response.json()
                return {
                    "success": True,
                    "file_id": result.get("id"),
                    "voucher_id": result.get("voucherId"),
                    "error": None
                }
            else:
                logger.error(f"Lexoffice upload failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Upload failed with status {response.status_code}"
                }

        except FileNotFoundError:
            logger.error(f"PDF file not found: {pdf_file_path}")
            return {
                "success": False,
                "error": "PDF file not found"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Lexoffice API error: {e}")
            return {
                "success": False,
                "error": f"API connection error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error uploading to Lexoffice: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    def health_check(self) -> bool:
        """Check if Lexoffice API is reachable"""
        if not self.api_key:
            return False
            
        try:
            response = requests.get(
                f"{self.api_url}/v1/profile",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False

    def get_profile(self) -> Optional[Dict]:
        """Get Lexoffice profile information"""
        if not self.api_key:
            return None

        try:
            response = requests.get(
                f"{self.api_url}/v1/profile",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
