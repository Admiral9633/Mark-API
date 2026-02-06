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
