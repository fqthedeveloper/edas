from django.db import models
from companies.models import Company
from templatesapp.models import Template

class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    default_template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, blank=True)
    default_fields = models.JSONField(default=dict)  # e.g., {"filter_media": "HDPE...", "moc": "ALUMINIUM"}

    def __str__(self):
        return self.name