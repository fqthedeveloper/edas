from django.db import models
from django.contrib.auth import get_user_model
from clients.models import Client
from products.models import Product
from templatesapp.models import Template
import json
from decimal import Decimal


User = get_user_model()

class Quotation(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    quotation_number = models.CharField(max_length=100, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True)
    date = models.DateField(auto_now_add=True)
    valid_until = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    terms = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=18)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    final_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.quotation_number

    def calculate_totals(self):
        """Recalculate all totals based on line items."""
        items = self.items.all()
        self.subtotal = sum(item.amount for item in items)
        self.discount_amount = (self.subtotal * self.discount_percent) / 100
        after_discount = self.subtotal - self.discount_amount
        self.tax_amount = (after_discount * self.tax_percent) / 100
        self.grand_total = after_discount + self.tax_amount + self.shipping_charge
        self.final_total = self.grand_total
        self.save()

class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
    sr_no = models.PositiveIntegerField()
    description = models.CharField(max_length=255)
    type = models.CharField(max_length=100, blank=True)
    flange_box = models.CharField(max_length=50, blank=True)
    cfm = models.PositiveIntegerField(null=True, blank=True)
    qty = models.PositiveIntegerField(default=1)
    unit_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Additional dimensions
    length = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.sr_no}. {self.description}"

    def save(self, *args, **kwargs):
        # Ensure qty and unit_rate are numeric before multiplication
        try:
            self.qty = int(self.qty)
        except (ValueError, TypeError):
            self.qty = 1
        try:
            self.unit_rate = Decimal(self.unit_rate)
        except (ValueError, TypeError):
            self.unit_rate = Decimal(0)

        self.amount = self.qty * self.unit_rate
        super().save(*args, **kwargs)
        self.quotation.calculate_totals()