from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .models import Template, TemplateField
from .forms import TemplateForm, TemplateFieldForm
from django.forms import inlineformset_factory

TemplateFieldFormSet = inlineformset_factory(
    Template, TemplateField,
    form=TemplateFieldForm,
    extra=1, can_delete=True
)

class TemplateListView(ListView):
    model = Template
    template_name = 'templatesapp/list.html'
    context_object_name = 'templates'

class TemplateCreateView(CreateView):
    model = Template
    form_class = TemplateForm
    template_name = 'templatesapp/form.html'
    success_url = reverse_lazy('template_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['field_formset'] = TemplateFieldFormSet(self.request.POST)
        else:
            context['field_formset'] = TemplateFieldFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        field_formset = context['field_formset']
        if field_formset.is_valid():
            self.object = form.save()
            field_formset.instance = self.object
            field_formset.save()
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)

class TemplateUpdateView(UpdateView):
    model = Template
    form_class = TemplateForm
    template_name = 'templatesapp/form.html'
    success_url = reverse_lazy('template_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['field_formset'] = TemplateFieldFormSet(self.request.POST, instance=self.object)
        else:
            context['field_formset'] = TemplateFieldFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        field_formset = context['field_formset']
        if field_formset.is_valid():
            self.object = form.save()
            field_formset.instance = self.object
            field_formset.save()
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)

class TemplateDeleteView(DeleteView):
    model = Template
    success_url = reverse_lazy('template_list')
    template_name = 'templatesapp/confirm_delete.html'