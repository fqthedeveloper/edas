from django import forms
from .models import Template, TemplateField
from dropdowns.models import DropdownList

class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = '__all__'
        widgets = {
            'company': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'template_type': forms.TextInput(attrs={'class': 'form-control'}),
            'page_size': forms.TextInput(attrs={'class': 'form-control'}),
            'orientation': forms.TextInput(attrs={'class': 'form-control'}),
            'html_layout': forms.Textarea(attrs={'rows': 16, 'class': 'form-control font-monospace', 'style': 'font-size: 9pt;'}),
            'header': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'footer': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'margins': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'preview_image': forms.FileInput(attrs={'class': 'form-control'}),
            'docx_template': forms.FileInput(attrs={'class': 'form-control'}),
            'logo_position': forms.TextInput(attrs={'class': 'form-control'}),
            'signature_position': forms.TextInput(attrs={'class': 'form-control'}),
            'qr_position': forms.TextInput(attrs={'class': 'form-control'}),
            'barcode_position': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TemplateFieldForm(forms.ModelForm):
    class Meta:
        model = TemplateField
        exclude = ['template']
        widgets = {
            'field_name': forms.TextInput(attrs={'class': 'form-control'}),
            'label': forms.TextInput(attrs={'class': 'form-control'}),
            'field_type': forms.Select(attrs={'class': 'form-select'}),
            'group': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'placeholder': forms.TextInput(attrs={'class': 'form-control'}),
            'default_value': forms.TextInput(attrs={'class': 'form-control'}),
            'tooltip': forms.TextInput(attrs={'class': 'form-control'}),
            'column_width': forms.NumberInput(attrs={'class': 'form-control'}),
            'dropdown': forms.Select(attrs={'class': 'form-select'}),
            'validation_rules': forms.Textarea(attrs={'rows': 2, 'class': 'form-control font-monospace'}),
            'formula_expression': forms.Textarea(attrs={'rows': 2, 'class': 'form-control font-monospace'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dropdown'].queryset = DropdownList.objects.all()
        self.fields['dropdown'].required = False