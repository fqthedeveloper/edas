import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from clients.models import Client
from products.models import Product
from templatesapp.models import Template, TemplateField
from .models import Document, DocumentValue
from .forms import build_dynamic_form
from .tasks import generate_document_pdf_docx
from sequences.services import get_next_number
from django.db.models import Q, Count
from django.utils import timezone
from django.template.loader import render_to_string



@login_required
def document_wizard_step1(request):
    clients = Client.objects.filter(is_active=True)
    return render(request, 'documents/step1.html', {'clients': clients})

@login_required
def document_wizard_step2(request):
    client_id = request.GET.get('client')
    if not client_id:
        return redirect('document_step1')
    client = get_object_or_404(Client, id=client_id)
    products = Product.objects.filter(company=client.company, default_template__isnull=False)
    return render(request, 'documents/step2.html', {'client': client, 'products': products})

@login_required
def document_wizard_step3(request):
    client_id = request.GET.get('client')
    product_id = request.GET.get('product')
    if not client_id or not product_id:
        return redirect('document_step1')
    client = get_object_or_404(Client, id=client_id)
    product = get_object_or_404(Product, id=product_id)
    template = product.default_template or client.default_template
    if not template:
        return render(request, 'documents/error.html', {'msg': 'No template defined for this product/client.'})

    # Build initial data
    initial = {}
    # Client fields
    initial['client_name'] = client.name
    initial['client_address'] = client.address
    initial['client_email'] = client.email
    initial['client_phone'] = client.phone
    initial['client_gst'] = client.gst
    initial['client_contact_person'] = client.contact_person

    # Product default fields (JSON)
    if product.default_fields:
        for key, val in product.default_fields.items():
            initial[key] = val

    # Auto date
    today = datetime.date.today()
    initial['date'] = today.isoformat()
    initial['testing_date'] = today.isoformat()

    # TC number
    prefix = 'AFPL/2026-27/'  # you can make this configurable
    next_num = get_next_number(prefix)
    initial['tc_number'] = f"{prefix}{next_num}"

    if request.method == 'POST':
        form_class = build_dynamic_form(template.id, data=request.POST)
        form = form_class(request.POST)
        if form.is_valid():
            # Convert form data to JSON-serializable format
            serializable_data = {}
            for key, value in form.cleaned_data.items():
                if isinstance(value, (datetime.date, datetime.datetime)):
                    serializable_data[key] = value.isoformat()
                else:
                    serializable_data[key] = value

            # Create document
            doc = Document.objects.create(
                client=client,
                product=product,
                template=template,
                document_number=initial['tc_number'],
                status='draft',
                created_by=request.user,
                form_data=serializable_data
            )
            for field_name, value in form.cleaned_data.items():
                tfield = TemplateField.objects.get(template=template, field_name=field_name)
                # Convert value to string for storage
                if isinstance(value, (datetime.date, datetime.datetime)):
                    str_value = value.isoformat()
                else:
                    str_value = str(value)
                DocumentValue.objects.create(document=doc, field=tfield, value=str_value)
            # Trigger generation asynchronously
            generate_document_pdf_docx.delay(doc.id)
            return redirect('document_status', doc.id)
        else:
            # re-render with errors
            return render(request, 'documents/step3.html', {'form': form, 'template': template})
    else:
        form_class = build_dynamic_form(template.id, initial=initial)
        form = form_class()
        return render(request, 'documents/step3.html', {'form': form, 'template': template})

@login_required
def document_status(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    return render(request, 'documents/status.html', {'doc': doc})

@login_required
def document_preview(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    context = {val.field.field_name: val.value for val in doc.values.all()}
    context['document'] = doc
    html = render_to_string(doc.template.html_layout, context)
    return HttpResponse(html)

@login_required
def document_list(request):
    docs = Document.objects.all().order_by('-created_at')
    return render(request, 'documents/list.html', {'documents': docs})

@login_required
def search_documents(request):
    q = request.GET.get('q', '')
    docs = Document.objects.filter(
        Q(document_number__icontains=q) |
        Q(client__name__icontains=q) |
        Q(product__name__icontains=q) |
        Q(template__name__icontains=q)
    )
    return render(request, 'documents/search.html', {'documents': docs, 'query': q})

@login_required
def dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)
    total_today = Document.objects.filter(created_at__date=today).count()
    total_month = Document.objects.filter(created_at__date__gte=month_start).count()
    pending = Document.objects.filter(status='draft').count()
    recent = Document.objects.order_by('-created_at')[:10]
    context = {
        'total_today': total_today,
        'total_month': total_month,
        'pending': pending,
        'recent': recent,
    }
    return render(request, 'dashboard.html', context)

def verify_document(request, document_number):
    doc = get_object_or_404(Document, document_number=document_number, status='generated')
    context = {val.field.field_name: val.value for val in doc.values.all()}
    context['document'] = doc
    return render(request, 'verification/verify.html', context)

@login_required
def download_pdf(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    if doc.generated_pdf:
        response = HttpResponse(doc.generated_pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{doc.document_number}.pdf"'
        return response
    return HttpResponse('PDF not ready yet', status=404)

@login_required
def download_docx(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    if doc.generated_docx:
        response = HttpResponse(doc.generated_docx.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="{doc.document_number}.docx"'
        return response
    return HttpResponse('DOCX not ready yet', status=404)