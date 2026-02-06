from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'created_at', 'updated_at', 'original_filename',
                  'pdf_file', 'marker_markdown', 'marker_json', 'status', 'error_message',
                  'ai_classification', 'is_invoice', 'invoice_type',
                  'invoice_number', 'invoice_date', 'due_date', 'total_amount', 'net_amount',
                  'tax_amount', 'currency', 'vendor_name', 'vendor_address', 'customer_name',
                  'lexoffice_sent', 'lexoffice_file_id', 'lexoffice_voucher_id', 'lexoffice_error']
        read_only_fields = ['id', 'created_at', 'updated_at', 'marker_markdown',
                           'marker_json', 'status', 'error_message',
                           'ai_classification', 'is_invoice', 'invoice_type',
                           'invoice_number', 'invoice_date', 'due_date', 'total_amount', 'net_amount',
                           'tax_amount', 'currency', 'vendor_name', 'vendor_address', 'customer_name',
                           'lexoffice_sent', 'lexoffice_file_id', 'lexoffice_voucher_id', 'lexoffice_error']

class DocumentUploadSerializer(serializers.Serializer):
    pdf_file = serializers.FileField()

    def validate_pdf_file(self, value):
        if not value.name.endswith('.pdf'):
            raise serializers.ValidationError("Nur PDF-Dateien sind erlaubt.")

        # Max 50MB
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("Datei ist zu groß. Maximum: 50MB")

        return value
