"""
Lexoffice API client for uploading vouchers (invoices)
"""
import os
import logging
import requests
import time
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

    def upload_voucher(self, pdf_file_path: str, voucher_type: str = "voucher", invoice_data: Dict = None, doc_invoice_type: str = None) -> Dict:
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
            doc_invoice_type: 'incoming' or 'outgoing' from AI classification
            
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
                    # Get or create contact first
                    contact_id = None
                    if doc_invoice_type == "outgoing":
                        contact_name = invoice_data.get("customer_name")
                        contact_address = None  # Customers don't have address in our extraction
                    else:
                        contact_name = invoice_data.get("vendor_name")
                        contact_address = invoice_data.get("vendor_address")
                    
                    if contact_name:
                        contact_id = self._get_or_create_contact(contact_name, doc_invoice_type, contact_address)
                    
                    update_success = self._update_voucher_data(voucher_id, file_id, invoice_data, doc_invoice_type, contact_id)
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

    def _update_voucher_data(self, voucher_id: str, file_id: str, invoice_data: Dict, doc_invoice_type: str = None, contact_id: str = None) -> bool:
        """
        Update voucher with extracted invoice data
        
        Args:
            voucher_id: Lexoffice voucher ID
            file_id: Lexoffice file ID
            invoice_data: Extracted invoice data from AI
            doc_invoice_type: 'incoming' or 'outgoing' from AI classification
            
        Returns:
            bool: Success status
        """
        try:
            # Determine Lexoffice voucher type based on our classification
            # incoming = we received invoice (purchaseinvoice)
            # outgoing = we sent invoice (salesinvoice)
            if doc_invoice_type == "incoming":
                lexoffice_type = "purchaseinvoice"
                default_category = "8f8664a8-fd86-11e1-a21f-0800200c9a66"  # Wareneinkauf
            else:  # outgoing or unknown
                lexoffice_type = "salesinvoice" 
                default_category = "8f8664a8-fd86-11e1-a21f-0800200c9a66"  # Default category
            
            # Build voucher data structure for Lexoffice API
            voucher_payload = {
                "type": lexoffice_type,
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
                        "categoryId": default_category
                    }
                ],
                "files": [file_id]
            }
            
            # Add contact info based on invoice type
            # Use contactId if we found/created the contact
            if contact_id:
                voucher_payload["contactId"] = contact_id
            else:
                # Fallback: try with contactName only
                if doc_invoice_type == "outgoing":
                    contact_name = invoice_data.get("customer_name") or invoice_data.get("vendor_name")
                else:
                    contact_name = invoice_data.get("vendor_name")
                
                if contact_name:
                    voucher_payload["contactName"] = contact_name
            
            # Remove None values
            voucher_payload = {k: v for k, v in voucher_payload.items() if v is not None}
            
            # Update voucher via Lexoffice API with retry logic
            max_retries = 3
            retry_delay = 2  # seconds
            
            for attempt in range(max_retries):
                response = requests.put(
                    f"{self.api_url}/v1/vouchers/{voucher_id}",
                    headers={**self.headers, "Content-Type": "application/json"},
                    json=voucher_payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    logger.info(f"Voucher {voucher_id} successfully updated with extracted data")
                    return True
                elif response.status_code == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Rate limit hit, waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Rate limit exceeded after {max_retries} retries")
                        return False
                else:
                    logger.warning(f"Voucher update failed: {response.status_code} - {response.text}")
                    return False
            
            return True
                
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

    def _get_or_create_contact(self, contact_name: str, invoice_type: str, contact_address: str = None) -> Optional[str]:
        """
        Search for existing contact or create new one
        
        Args:
            contact_name: Name of the contact to search/create
            invoice_type: 'incoming' or 'outgoing'
            contact_address: Full address string (e.g., "Straße 1, 12345 Stadt")
            
        Returns:
            Contact ID if found/created, None otherwise
        """
        try:
            # Step 1: Search for existing contact
            logger.info(f"Searching for contact: {contact_name}")
            search_response = requests.get(
                f"{self.api_url}/v1/contacts",
                headers=self.headers,
                params={"name": contact_name},
                timeout=10
            )
            
            if search_response.status_code == 200:
                contacts = search_response.json().get("content", [])
                if contacts:
                    contact_id = contacts[0].get("id")
                    logger.info(f"Found existing contact: {contact_name} (ID: {contact_id})")
                    return contact_id
            
            # Step 2: Contact not found, create new one
            logger.info(f"Contact not found, creating new: {contact_name}")
            
            # Determine contact role based on invoice type
            if invoice_type == "outgoing":
                roles = {"customer": {}}
            else:
                roles = {"vendor": {}}
            
            contact_payload = {
                "version": 0,
                "roles": roles,
                "company": {
                    "name": contact_name
                }
            }
            
            # Add address if provided
            if contact_address:
                # Parse address (simple split on comma)
                address_parts = [part.strip() for part in contact_address.split(',')]
                
                address_data = {}
                if len(address_parts) >= 1:
                    # First part is usually street
                    address_data["street"] = address_parts[0]
                if len(address_parts) >= 2:
                    # Try to extract zip and city from last part
                    last_part = address_parts[-1].strip()
                    parts = last_part.split(' ', 1)
                    if len(parts) == 2:
                        address_data["zip"] = parts[0]
                        address_data["city"] = parts[1]
                    else:
                        address_data["city"] = last_part
                
                address_data["countryCode"] = "DE"
                
                contact_payload["addresses"] = {
                    "billing": [address_data]
                }
            
            # Create contact with retry logic for rate limits
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                create_response = requests.post(
                    f"{self.api_url}/v1/contacts",
                    headers={**self.headers, "Content-Type": "application/json"},
                    json=contact_payload,
                    timeout=10
                )
                
                if create_response.status_code == 200:
                    contact_id = create_response.json().get("id")
                    logger.info(f"Created new contact: {contact_name} (ID: {contact_id})")
                    return contact_id
                elif create_response.status_code == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        logger.warning(f"Rate limit hit when creating contact, waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Failed to create contact after {max_retries} retries: Rate limit exceeded")
                        return None
                else:
                    logger.error(f"Failed to create contact: {create_response.status_code} - {create_response.text}")
                    return None
            
            return None
                
        except Exception as e:
            logger.error(f"Error in get_or_create_contact: {e}")
            return None

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
