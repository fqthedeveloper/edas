from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Template, TemplateField
from .forms import TemplateForm, TemplateFieldForm

# ---------- Template CRUD ----------
class TemplateListView(ListView):
    model = Template
    template_name = 'templatesapp/list.html'
    context_object_name = 'templates'

class TemplateCreateView(CreateView):
    model = Template
    form_class = TemplateForm
    template_name = 'templatesapp/form.html'
    success_url = reverse_lazy('template_list')

class TemplateUpdateView(UpdateView):
    model = Template
    form_class = TemplateForm
    template_name = 'templatesapp/form.html'
    success_url = reverse_lazy('template_list')

class TemplateDeleteView(DeleteView):
    model = Template
    success_url = reverse_lazy('template_list')
    template_name = 'templatesapp/confirm_delete.html'


# ---------- Template Fields CRUD ----------
class TemplateFieldListView(ListView):
    model = TemplateField
    template_name = 'templatesapp/field_list.html'
    context_object_name = 'fields'

    def get_queryset(self):
        self.template = get_object_or_404(Template, pk=self.kwargs['template_pk'])
        return TemplateField.objects.filter(template=self.template).order_by('order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['template'] = self.template
        return context

class TemplateFieldCreateView(CreateView):
    model = TemplateField
    form_class = TemplateFieldForm
    template_name = 'templatesapp/field_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.template = get_object_or_404(Template, pk=self.kwargs['template_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['template'] = self.template
        return context

    def form_valid(self, form):
        form.instance.template = self.template
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('template_field_list', kwargs={'template_pk': self.template.pk})

class TemplateFieldUpdateView(UpdateView):
    model = TemplateField
    form_class = TemplateFieldForm
    template_name = 'templatesapp/field_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['template'] = self.object.template
        return context

    def get_success_url(self):
        return reverse('template_field_list', kwargs={'template_pk': self.object.template.pk})

class TemplateFieldDeleteView(DeleteView):
    model = TemplateField
    template_name = 'templatesapp/field_confirm_delete.html'

    def get_success_url(self):
        return reverse('template_field_list', kwargs={'template_pk': self.object.template.pk})