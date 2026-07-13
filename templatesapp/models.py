from django.db import models
from companies.models import Company

class Template(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    template_type = models.CharField(max_length=50, default='Test Certificate')
    preview_image = models.ImageField(upload_to='template_previews/', blank=True, null=True)
    html_layout = models.TextField(help_text="Full HTML with placeholders like {{client_name}}")
    docx_template = models.FileField(upload_to='template_docx/', help_text="Original DOCX with placeholders")
    header = models.TextField(blank=True)
    footer = models.TextField(blank=True)
    page_size = models.CharField(max_length=20, default='A4')
    orientation = models.CharField(max_length=10, default='portrait')
    margins = models.JSONField(default=dict)
    logo_position = models.CharField(max_length=50, default='top-left')
    signature_position = models.CharField(max_length=50, default='bottom-right')
    qr_position = models.CharField(max_length=50, default='bottom-left')
    barcode_position = models.CharField(max_length=50, default='bottom-center')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class TemplateField(models.Model):
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('dropdown', 'Dropdown'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio'),
        ('textarea', 'Textarea'),
        ('image', 'Image'),
        ('signature', 'Signature'),
        ('formula', 'Formula'),
        ('auto_number', 'Auto Number'),
        ('auto_date', 'Auto Date'),
        ('hidden', 'Hidden'),
        ('readonly', 'Read Only'),
        ('file_upload', 'File Upload'),
    ]
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='fields')
    field_name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES)
    placeholder = models.CharField(max_length=255, blank=True)
    validation_rules = models.JSONField(default=dict, blank=True, null=True)
    default_value = models.CharField(max_length=255, blank=True)
    tooltip = models.CharField(max_length=255, blank=True)
    group = models.CharField(max_length=100, blank=True)
    column_width = models.PositiveIntegerField(default=12)
    order = models.PositiveIntegerField()
    is_visible = models.BooleanField(default=True)
    is_editable = models.BooleanField(default=True)
    is_printable = models.BooleanField(default=True)
    is_searchable = models.BooleanField(default=False)
    is_exportable = models.BooleanField(default=False)
    dropdown = models.ForeignKey('dropdowns.DropdownList', on_delete=models.SET_NULL, null=True, blank=True)
    formula_expression = models.TextField(blank=True, help_text="e.g., air_velocity = airflow / area")

    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return self.label