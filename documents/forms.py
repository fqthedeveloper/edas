from django import forms
from templatesapp.models import TemplateField
from templatesapp.models import Template
from dropdowns.models import DropdownList

def build_dynamic_form(template_id, data=None, initial=None):
    template_fields = list(TemplateField.objects.filter(template_id=template_id, is_visible=True).order_by('order'))

    class DynamicForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in template_fields:
                validation_rules = field.validation_rules or {}
                required = validation_rules.get('required', False)
                form_field = None

                if field.field_type == 'text':
                    w_kwargs = {'class': 'form-control'}
                    if field.placeholder:
                        w_kwargs['placeholder'] = field.placeholder
                    form_field = forms.CharField(
                        required=required,
                        label=field.label,
                        widget=forms.TextInput(attrs=w_kwargs)
                    )
                elif field.field_type == 'number':
                    form_field = forms.FloatField(
                        required=required,
                        label=field.label,
                        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'})
                    )
                elif field.field_type == 'date':
                    form_field = forms.DateField(
                        required=required,
                        label=field.label,
                        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
                    )
                elif field.field_type == 'dropdown':
                    choices = [(item, item) for item in field.dropdown.items] if field.dropdown else []
                    form_field = forms.ChoiceField(
                        required=required,
                        label=field.label,
                        choices=choices,
                        widget=forms.Select(attrs={'class': 'form-select'})
                    )
                elif field.field_type == 'checkbox':
                    form_field = forms.BooleanField(
                        required=False,
                        label=field.label,
                        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
                    )
                elif field.field_type == 'textarea':
                    form_field = forms.CharField(
                        required=required,
                        label=field.label,
                        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
                    )
                elif field.field_type == 'formula':
                    form_field = forms.CharField(
                        required=False,
                        label=field.label,
                        widget=forms.TextInput(attrs={'readonly': True, 'class': 'form-control bg-light font-monospace'})
                    )
                else:
                    form_field = forms.CharField(
                        required=required,
                        label=field.label,
                        widget=forms.TextInput(attrs={'class': 'form-control'})
                    )

                if initial and field.field_name in initial:
                    form_field.initial = initial[field.field_name]
                elif field.default_value:
                    form_field.initial = field.default_value

                self.fields[field.field_name] = form_field

    return DynamicForm


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Select Excel file (.xlsx)',
        help_text='Must be .xlsx format'
    )
    template = forms.ModelChoiceField(
        queryset=Template.objects.filter(is_active=True),
        required=False,
        help_text='Default template for rows that do not specify one'
    )