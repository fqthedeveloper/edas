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
        fields = '__all__'
        exclude = ['template']
        widgets = {
            'validation_rules': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dropdown'].queryset = DropdownList.objects.all()