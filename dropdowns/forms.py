from django import forms
from .models import DropdownList

class DropdownListForm(forms.ModelForm):
    items = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), help_text='One item per line')

    def clean_items(self):
        data = self.cleaned_data['items']
        items = [line.strip() for line in data.splitlines() if line.strip()]
        return items

    class Meta:
        model = DropdownList
        fields = ['name', 'items']