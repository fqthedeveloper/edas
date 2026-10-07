from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from companies.models import Company
from .models import Template, TemplateField
from .forms import TemplateForm, TemplateFieldForm
from .ai_importer import DocumentLayoutAnalyzer
import json


# ---------- Template CRUD ----------
@method_decorator(login_required, name='dispatch')
class TemplateListView(ListView):
    model = Template
    template_name = 'templatesapp/list.html'
    context_object_name = 'templates'

@method_decorator(login_required, name='dispatch')
class TemplateCreateView(CreateView):
    model = Template
    form_class = TemplateForm
    template_name = 'templatesapp/form.html'
    success_url = reverse_lazy('template_list')

@method_decorator(login_required, name='dispatch')
class TemplateUpdateView(UpdateView):
    model = Template
    form_class = TemplateForm
    template_name = 'templatesapp/form.html'
    success_url = reverse_lazy('template_list')

@method_decorator(login_required, name='dispatch')
class TemplateDeleteView(DeleteView):
    model = Template
    success_url = reverse_lazy('template_list')
    template_name = 'templatesapp/confirm_delete.html'


# ---------- Template Fields CRUD ----------
@method_decorator(login_required, name='dispatch')
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

@method_decorator(login_required, name='dispatch')
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

@method_decorator(login_required, name='dispatch')
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

@method_decorator(login_required, name='dispatch')
class TemplateFieldDeleteView(DeleteView):
    model = TemplateField
    template_name = 'templatesapp/field_confirm_delete.html'

    def get_success_url(self):
        return reverse('template_field_list', kwargs={'template_pk': self.object.template.pk})


# ---------- AI / Automated Document Importer Views ----------
@login_required
def ai_import_upload(request):
    """
    Renders file upload page for PDF / Word documents,
    and analyzes the uploaded file to extract layout, tables, and fields.
    """
    if request.method == 'POST' and request.FILES.get('document_file'):
        uploaded_file = request.FILES['document_file']
        filename = uploaded_file.name

        try:
            file_bytes = uploaded_file.read()
            analyzer = DocumentLayoutAnalyzer(file_bytes, filename)
            analysis = analyzer.parse()
            
            # Store in session for confirmation
            request.session['ai_template_analysis'] = {
                'filename': filename,
                'template_name': analysis['template_name'],
                'fields': analysis['fields'],
                'sections': analysis['sections'],
                'html_layout': analysis['html_layout']
            }
            return redirect('ai_template_preview')
        except Exception as e:
            messages.error(request, f"Error analyzing document: {e}")
            return redirect('ai_template_import')

    return render(request, 'templatesapp/ai_import.html')


@login_required
def ai_import_preview(request):
    """
    Displays the extracted layout preview and fields list for admin review/editing.
    """
    analysis = request.session.get('ai_template_analysis')
    if not analysis:
        messages.warning(request, "No document currently analyzed. Please upload a document first.")
        return redirect('ai_template_import')

    return render(request, 'templatesapp/ai_preview.html', {
        'analysis': analysis
    })


@login_required
@require_POST
def ai_import_save(request):
    """
    Saves the analyzed design as an active Template and generates TemplateField records.
    """
    analysis = request.session.get('ai_template_analysis')
    if not analysis:
        messages.error(request, "Session expired or no template analysis found.")
        return redirect('ai_template_import')

    template_name = request.POST.get('template_name', analysis['template_name']).strip()
    html_layout = request.POST.get('html_layout', analysis['html_layout']).strip()
    
    company = Company.objects.first()
    if not company:
        company = Company.objects.create(name="Default Organization")

    # Create Template
    template = Template.objects.create(
        company=company,
        name=template_name,
        template_type='certificate',
        html_layout=html_layout,
        is_active=True
    )

    # Create TemplateFields
    fields_data = analysis.get('fields', [])
    created_fields = 0
    for idx, f in enumerate(fields_data, start=1):
        field_name = f.get('field_name')
        label = f.get('label') or field_name.replace('_', ' ').title()
        field_type = f.get('field_type', 'text')
        section = f.get('section', 'General Information')

        TemplateField.objects.create(
            template=template,
            field_name=field_name,
            label=label,
            field_type=field_type,
            group=section,
            order=idx,
            is_visible=True,
            is_editable=True,
            is_printable=True
        )
        created_fields += 1

    # Clear session
    del request.session['ai_template_analysis']

    messages.success(request, f"Template '{template.name}' successfully created with {created_fields} dynamic fields!")
    return redirect('template_field_list', template_pk=template.pk)