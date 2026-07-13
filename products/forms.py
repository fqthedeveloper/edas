from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'default_fields': forms.Textarea(attrs={'rows': 5, 'class': 'font-monospace'}),
        }