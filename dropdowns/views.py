from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import DropdownList
from .forms import DropdownListForm

class DropdownListView(ListView):
    model = DropdownList
    template_name = 'dropdowns/list.html'
    context_object_name = 'dropdowns'

class DropdownCreateView(CreateView):
    model = DropdownList
    form_class = DropdownListForm
    template_name = 'dropdowns/form.html'
    success_url = reverse_lazy('dropdown_list')

class DropdownUpdateView(UpdateView):
    model = DropdownList
    form_class = DropdownListForm
    template_name = 'dropdowns/form.html'
    success_url = reverse_lazy('dropdown_list')

class DropdownDeleteView(DeleteView):
    model = DropdownList
    success_url = reverse_lazy('dropdown_list')
    template_name = 'dropdowns/confirm_delete.html'