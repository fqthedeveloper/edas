from django.db import models
from companies.models import Company
from templatesapp.models import Template
from products.models import Product

class Client(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    gst = models.CharField(max_length=20, blank=True)
    contact_person = models.CharField(max_length=255)
    default_template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, blank=True)
    default_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name