from django import forms
from templatesapp.models import TemplateField
from templatesapp.models import Template
from dropdowns.models import DropdownList

def build_dynamic_form(template_id, data=None, initial=None):
    fields = TemplateField.objects.filter(template_id=template_id, is_visible=True).order_by('order')
    class DynamicForm(forms.Form):
        pass
    for field in fields:
        validation_rules = field.validation_rules or {}
        required = validation_rules.get('required', False)

        if field.field_type == 'text':
            kwargs = {'required': required, 'label': field.label}
            if field.placeholder:
                kwargs['widget'] = forms.TextInput(attrs={'placeholder': field.placeholder})
            DynamicForm.base_fields[field.field_name] = forms.CharField(**kwargs)
        elif field.field_type == 'number':
            kwargs = {'required': required, 'label': field.label}
            DynamicForm.base_fields[field.field_name] = forms.FloatField(**kwargs)
        elif field.field_type == 'date':
            kwargs = {'required': required, 'label': field.label}
            DynamicForm.base_fields[field.field_name] = forms.DateField(
                widget=forms.DateInput(attrs={'type': 'date'}), **kwargs
            )
        elif field.field_type == 'dropdown':
            if field.dropdown:
                choices = [(item, item) for item in field.dropdown.items]
            else:
                choices = []
            kwargs = {'required': required, 'label': field.label, 'choices': choices}
            DynamicForm.base_fields[field.field_name] = forms.ChoiceField(
                widget=forms.Select(attrs={'class': 'form-select'}), **kwargs
            )
        elif field.field_type == 'checkbox':
            kwargs = {'required': False, 'label': field.label}
            DynamicForm.base_fields[field.field_name] = forms.BooleanField(**kwargs)
        elif field.field_type == 'textarea':
            kwargs = {'required': required, 'label': field.label}
            DynamicForm.base_fields[field.field_name] = forms.CharField(
                widget=forms.Textarea(attrs={'rows': 3}), **kwargs
            )
        elif field.field_type == 'formula':
            kwargs = {'required': False, 'label': field.label}
            DynamicForm.base_fields[field.field_name] = forms.CharField(
                widget=forms.TextInput(attrs={'readonly': True}), **kwargs
            )
        else:
            kwargs = {'required': required, 'label': field.label}
            DynamicForm.base_fields[field.field_name] = forms.CharField(**kwargs)

        if initial and field.field_name in initial:
            DynamicForm.base_fields[field.field_name].initial = initial[field.field_name]
        elif field.default_value:
            DynamicForm.base_fields[field.field_name].initial = field.default_value

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