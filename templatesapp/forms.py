from django import forms
from .models import Template, TemplateField
from dropdowns.models import DropdownList

class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = '__all__'
        widgets = {
            'html_layout': forms.Textarea(attrs={'rows': 15, 'class': 'font-monospace'}),
            'margins': forms.Textarea(attrs={'rows': 3}),
        }

class TemplateFieldForm(forms.ModelForm):
    class Meta:
        model = TemplateField
        exclude = ['template']
        widgets = {
            'validation_rules': forms.Textarea(attrs={'rows': 3}),
            'formula_expression': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit dropdown choices to those available for the company (optional)
        self.fields['dropdown'].queryset = DropdownList.objects.all()
        self.fields['dropdown'].required = False