from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'original_filename', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['original_filename']
    readonly_fields = ['created_at', 'updated_at']
