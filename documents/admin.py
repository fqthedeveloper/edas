from django.contrib import admin
from .models import Document, DocumentValue

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['document_number', 'client', 'product', 'status', 'created_at']
    search_fields = ['document_number', 'client__name']
    list_filter = ['status', 'created_at']

@admin.register(DocumentValue)
class DocumentValueAdmin(admin.ModelAdmin):
    list_display = ['document', 'field', 'value']