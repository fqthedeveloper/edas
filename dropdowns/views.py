from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import DropdownList
from .forms import DropdownListForm
from companies.models import Company  # <-- ADD THIS IMPORT

class DropdownListView(ListView):
    model = DropdownList
    template_name = 'dropdowns/list.html'
    context_object_name = 'dropdowns'

class DropdownCreateView(CreateView):
    model = DropdownList
    form_class = DropdownListForm
    template_name = 'dropdowns/form.html'
    success_url = reverse_lazy('dropdown_list')

    def form_valid(self, form):
        company = Company.objects.first()
        if company:
            form.instance.company = company
        else:
            form.add_error(None, "No company found. Please create a company first.")
            return self.form_invalid(form)
        return super().form_valid(form)

class DropdownUpdateView(UpdateView):
    model = DropdownList
    form_class = DropdownListForm
    template_name = 'dropdowns/form.html'
    success_url = reverse_lazy('dropdown_list')

class DropdownDeleteView(DeleteView):
    model = DropdownList
    success_url = reverse_lazy('dropdown_list')
    template_name = 'dropdowns/confirm_delete.html'