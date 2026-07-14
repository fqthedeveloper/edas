from django import forms
from .models import Quotation, QuotationItem

class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = [
            'client', 'product', 'template', 'valid_until',
            'discount_percent', 'tax_percent', 'shipping_charge',
            'notes', 'terms'
        ]
        widgets = {
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'terms': forms.Textarea(attrs={'rows': 5}),
        }

class QuotationItemForm(forms.ModelForm):
    class Meta:
        model = QuotationItem
        exclude = ['quotation', 'amount']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.TextInput(attrs={'class': 'form-control'}),
            'flange_box': forms.TextInput(attrs={'class': 'form-control'}),
            'cfm': forms.NumberInput(attrs={'class': 'form-control'}),
            'qty': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'length': forms.NumberInput(attrs={'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'class': 'form-control'}),
            'width': forms.NumberInput(attrs={'class': 'form-control'}),
        }