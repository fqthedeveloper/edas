from django.db import models
from clients.models import Client
from products.models import Product
from templatesapp.models import Template, TemplateField
from accounts.models import User

class Document(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('generated', 'Generated'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    document_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    generated_pdf = models.FileField(upload_to='generated/pdf/', blank=True, null=True)
    generated_docx = models.FileField(upload_to='generated/docx/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='generated/qr/', blank=True, null=True)
    barcode = models.ImageField(upload_to='generated/barcode/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    form_data = models.JSONField(default=dict)  # full data for audit
    sent_email = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.document_number

class DocumentValue(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='values')
    field = models.ForeignKey(TemplateField, on_delete=models.CASCADE)
    value = models.TextField()

    class Meta:
        unique_together = ['document', 'field']