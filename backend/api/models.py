from django.db import models

class Document(models.Model):
    """Model für hochgeladene PDF-Dokumente und deren OCR-Ergebnisse"""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    original_filename = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to='pdfs/')

    # OCR Ergebnisse von Marker
    marker_markdown = models.TextField(blank=True, null=True)
    marker_json = models.JSONField(blank=True, null=True)

    # AI Classification
    ai_classification = models.JSONField(blank=True, null=True, help_text="Ollama AI classification result")
    is_invoice = models.BooleanField(default=False, help_text="AI detected this as an invoice")
    invoice_type = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ('incoming', 'Eingangsrechnung (zu bezahlen)'),
            ('outgoing', 'Ausgangsrechnung (von mir)')
        ],
        help_text="Type of invoice: incoming or outgoing"
    )

    # Extracted Invoice Data
    invoice_number = models.CharField(max_length=100, blank=True, null=True, help_text="Rechnungsnummer")
    invoice_date = models.DateField(blank=True, null=True, help_text="Rechnungsdatum")
    due_date = models.DateField(blank=True, null=True, help_text="Fälligkeitsdatum")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Gesamtbetrag brutto")
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Nettobetrag")
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Umsatzsteuer")
    currency = models.CharField(max_length=3, default='EUR', help_text="Währung")
    vendor_name = models.CharField(max_length=255, blank=True, null=True, help_text="Lieferant/Absender")
    vendor_address = models.TextField(blank=True, null=True, help_text="Lieferantenadresse")
    customer_name = models.CharField(max_length=255, blank=True, null=True, help_text="Kunde/Empfänger")
    customer_address = models.TextField(blank=True, null=True, help_text="Kundenadresse")

    # Lexoffice Integration
    lexoffice_sent = models.BooleanField(default=False, help_text="Uploaded to Lexoffice")
    lexoffice_file_id = models.CharField(max_length=100, blank=True, null=True, help_text="Lexoffice file ID")
    lexoffice_voucher_id = models.CharField(max_length=100, blank=True, null=True, help_text="Lexoffice voucher ID")
    lexoffice_error = models.TextField(blank=True, null=True, help_text="Lexoffice upload error message")

    # Status
    STATUS_CHOICES = [
        ('uploaded', 'Hochgeladen'),
        ('processing', 'Wird verarbeitet'),
        ('completed', 'Abgeschlossen'),
        ('error', 'Fehler'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.original_filename} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

