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

    def upload_voucher(self, pdf_file_path: str, voucher_type: str = "voucher", invoice_data: Dict = None) -> Dict:
        """
        Upload a voucher (invoice) to Lexoffice with pre-filled data
        
        Args:
            pdf_file_path: Path to the PDF file
            voucher_type: Type of voucher (default: "voucher" for bookkeeping)
            invoice_data: Optional dict with invoice details:
                - invoice_number: Rechnungsnummer
                - invoice_date: Rechnungsdatum (YYYY-MM-DD)
                - due_date: Fälligkeitsdatum (YYYY-MM-DD)
                - total_amount: Gesamtbetrag
                - vendor_name: Lieferantenname
                - etc.
            
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
            # Step 1: Upload PDF file first
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
                file_id = result.get("id")
                voucher_id = result.get("voucherId")
                
                # Step 2: If invoice_data provided, update voucher with extracted data
                if invoice_data and voucher_id:
                    update_success = self._update_voucher_data(voucher_id, file_id, invoice_data)
                    if not update_success:
                        logger.warning(f"Voucher uploaded but data update failed for {voucher_id}")
                
                return {
                    "success": True,
                    "file_id": file_id,
                    "voucher_id": voucher_id,
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

    def _update_voucher_data(self, voucher_id: str, file_id: str, invoice_data: Dict) -> bool:
        """
        Update voucher with extracted invoice data
        
        Args:
            voucher_id: Lexoffice voucher ID
            file_id: Lexoffice file ID
            invoice_data: Extracted invoice data from AI
            
        Returns:
            bool: Success status
        """
        try:
            # Build voucher data structure for Lexoffice API
            voucher_payload = {
                "voucherNumber": invoice_data.get("invoice_number"),
                "voucherDate": invoice_data.get("invoice_date"),
                "dueDate": invoice_data.get("due_date"),
                "totalGrossAmount": invoice_data.get("total_amount"),
                "totalTaxAmount": invoice_data.get("tax_amount"),
                "taxType": "gross",
                "useCollectiveContact": False,
                "remark": f"Automatisch extrahiert durch KI",
                "voucherItems": [
                    {
                        "amount": invoice_data.get("net_amount") or invoice_data.get("total_amount"),
                        "taxAmount": invoice_data.get("tax_amount") or 0,
                        "taxRatePercent": self._calculate_tax_rate(
                            invoice_data.get("total_amount"),
                            invoice_data.get("tax_amount")
                        ),
                        "categoryId": None  # Lexoffice will auto-assign
                    }
                ],
                "files": [file_id]
            }
            
            # Add vendor/contact info if available
            if invoice_data.get("vendor_name"):
                voucher_payload["contactName"] = invoice_data.get("vendor_name")
            
            # Remove None values
            voucher_payload = {k: v for k, v in voucher_payload.items() if v is not None}
            
            # Update voucher via Lexoffice API
            response = requests.put(
                f"{self.api_url}/v1/vouchers/{voucher_id}",
                headers={**self.headers, "Content-Type": "application/json"},
                json=voucher_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Voucher {voucher_id} successfully updated with extracted data")
                return True
            else:
                logger.warning(f"Voucher update failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating voucher data: {e}")
            return False

    def _calculate_tax_rate(self, total: float, tax: float) -> int:
        """Calculate tax rate percentage from amounts"""
        if not total or not tax:
            return 19  # Default German VAT
        try:
            net = total - tax
            rate = (tax / net) * 100
            # Round to common German tax rates
            if rate < 10:
                return 7
            else:
                return 19
        except:
            return 19

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
