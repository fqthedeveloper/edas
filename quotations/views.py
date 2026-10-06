import datetime
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template import Template as DjangoTemplate, Context
from django.db import transaction
from django.core.paginator import Paginator
from django.conf import settings
from .models import Quotation, QuotationItem
from .forms import QuotationForm
from clients.models import Client
from products.models import Product
from templatesapp.models import Template
from sequences.services import get_next_number
from documents.services import image_to_base64  # <-- Import


@login_required
def quotation_list(request):
    quotations = Quotation.objects.all().order_by('-created_at')
    return render(request, 'quotations/list.html', {'quotations': quotations})

@login_required
def quotation_create(request):
    if request.method == 'POST':
        form = QuotationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                quotation = form.save(commit=False)
                prefix = 'AFT/2026-27/'
                next_num = get_next_number(prefix)
                quotation.quotation_number = f"{prefix}{next_num}"
                quotation.created_by = request.user
                quotation.save()
                return redirect('quotation_edit_items', quotation.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = QuotationForm()
    return render(request, 'quotations/form.html', {'form': form})

@login_required
def quotation_edit_items(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    if request.method == 'POST':
        descriptions = request.POST.getlist('description')
        types = request.POST.getlist('type')
        flange_boxes = request.POST.getlist('flange_box')
        cfms = request.POST.getlist('cfm')
        qtys = request.POST.getlist('qty')
        unit_rates = request.POST.getlist('unit_rate')
        lengths = request.POST.getlist('length')
        heights = request.POST.getlist('height')
        widths = request.POST.getlist('width')

        quotation.items.all().delete()

        for i in range(len(descriptions)):
            desc = descriptions[i].strip()
            if not desc:
                continue

            try:
                qty = int(qtys[i]) if qtys[i] else 1
            except (ValueError, TypeError):
                qty = 1

            try:
                unit_rate = Decimal(unit_rates[i]) if unit_rates[i] else Decimal(0)
            except (ValueError, TypeError):
                unit_rate = Decimal(0)

            try:
                cfm = int(cfms[i]) if cfms[i] else 0
            except (ValueError, TypeError):
                cfm = 0

            def parse_decimal(val):
                try:
                    return Decimal(val) if val else None
                except (ValueError, TypeError):
                    return None

            length = parse_decimal(lengths[i]) if i < len(lengths) else None
            height = parse_decimal(heights[i]) if i < len(heights) else None
            width = parse_decimal(widths[i]) if i < len(widths) else None

            QuotationItem.objects.create(
                quotation=quotation,
                sr_no=i+1,
                description=desc,
                type=types[i] if i < len(types) else '',
                flange_box=flange_boxes[i] if i < len(flange_boxes) else '',
                cfm=cfm,
                qty=qty,
                unit_rate=unit_rate,
                length=length,
                height=height,
                width=width,
            )

        quotation.calculate_totals()
        messages.success(request, 'Quotation items updated successfully.')
        return redirect('quotation_detail', quotation.pk)

    else:
        items = quotation.items.all()
        return render(request, 'quotations/edit_items.html', {'quotation': quotation, 'items': items})

@login_required
def quotation_detail(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    return render(request, 'quotations/detail.html', {'quotation': quotation})

@login_required
def quotation_pdf(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    company = quotation.client.company

    # Convert images to base64
    logo_b64 = image_to_base64(company.logo)
    signature_b64 = image_to_base64(company.signature)

    context = {
        'quotation': quotation,
        'items': quotation.items.all(),
        'company': company,
        'client': quotation.client,
        'subtotal': quotation.subtotal,
        'discount_amount': quotation.discount_amount,
        'grand_total': quotation.grand_total,
        'tax_amount': quotation.tax_amount,
        'final_total': quotation.final_total,
        'discount_percent': quotation.discount_percent,
        'tax_percent': quotation.tax_percent,
        'shipping_charge': quotation.shipping_charge,
        'base_url': getattr(settings, 'BASE_URL', 'http://localhost:8000'),
        'logo_b64': logo_b64,
        'signature_b64': signature_b64,
        'watermark_b64': logo_b64,   # <-- ADD THIS
        'has_watermark': bool(logo_b64)  # <-- ADD THIS
    }

    html = DjangoTemplate(QUOTATION_HTML_TEMPLATE).render(Context(context))
    from documents.services import generate_pdf_from_html
    pdf_bytes = generate_pdf_from_html(html, base_url=context.get('base_url'))
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{quotation.quotation_number}.pdf"'
    return response

# HTML template for quotation PDF (with base64 support)

QUOTATION_HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Quotation</title>
    <style>
        @page { size: A4; margin: 10mm; }
        body {
            font-family: Arial, sans-serif;
            font-size: 10pt;
            position: relative;
        }
        /* ----- Watermark ----- */
        .watermark {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
            display: flex;
            justify-content: center;
            align-items: center;
            opacity: 0.15; /* Adjust as needed */
        }
        .watermark img {
            width: 70%;
            height: auto;
            max-height: 70%;
            object-fit: contain;
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #0070c0;
            padding-bottom: 5px;
        }
        .header img {
            height: 50px;
        }
        .title {
            text-align: center;
            font-size: 16pt;
            font-weight: bold;
            color: #0070c0;
            margin: 10px 0;
        }
        .info-table {
            width: 100%;
            margin: 10px 0;
        }
        .info-table td {
            padding: 3px;
        }
        table.items {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        table.items th, table.items td {
            border: 1px solid #000;
            padding: 4px;
            text-align: center;
        }
        table.items th {
            background: #f0f0f0;
        }
        .totals {
            text-align: right;
            margin-top: 10px;
        }
        .footer {
            margin-top: 20px;
            font-size: 9pt;
            border-top: 1px solid #ccc;
            padding-top: 5px;
            text-align: center;
        }
        .terms {
            margin-top: 15px;
            font-size: 9pt;
        }
        .signature {
            text-align: right;
            margin-top: 20px;
        }
    </style>
</head>
<body>

    <!-- WATERMARK -->
    {% if has_watermark and watermark_b64 %}
    <div class="watermark">
        <img src="{{ watermark_b64 }}" alt="Watermark">
    </div>
    {% endif %}

    <!-- HEADER -->
    <div class="header">
        {% if logo_b64 %}
            <img src="{{ logo_b64 }}" alt="Logo">
        {% elif company.logo %}
            <img src="{{ base_url }}{{ company.logo.url }}" alt="Logo">
        {% else %}
            <span style="font-size:18pt; font-weight:bold; color:#218a8d;">AIR FILTER</span>
        {% endif %}
        <span style="font-size:18pt; font-weight:bold; color:#218a8d;">AIR FILTER</span>
    </div>

    <div class="title">QUOTATION</div>

    <table class="info-table">
        <tr><td><strong>Quotation No:</strong> {{ quotation.quotation_number }}</td><td><strong>Date:</strong> {{ quotation.date|date:"d-m-Y" }}</td></tr>
        <tr><td><strong>Client:</strong> {{ client.name }}</td><td><strong>Valid Until:</strong> {{ quotation.valid_until|date:"d-m-Y" }}</td></tr>
        <tr><td colspan="2"><strong>Address:</strong> {{ client.address }}</td></tr>
        <tr><td colspan="2"><strong>GST:</strong> {{ client.gst }}</td></tr>
    </table>

    <table class="items">
        <thead>
            <tr><th>#</th><th>Description</th><th>Type</th><th>Flange/Box</th><th>CFM</th><th>Qty</th><th>Unit Rate</th><th>Amount</th></tr>
        </thead>
        <tbody>
            {% for item in items %}
            <tr>
                <td>{{ forloop.counter }}</td>
                <td>{{ item.description }}</td>
                <td>{{ item.type }}</td>
                <td>{{ item.flange_box }}</td>
                <td>{{ item.cfm }}</td>
                <td>{{ item.qty }}</td>
                <td>{{ item.unit_rate }}</td>
                <td>{{ item.amount }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <div class="totals">
        <p><strong>Subtotal:</strong> {{ subtotal }}</p>
        <p><strong>Discount ({{ discount_percent }}%):</strong> {{ discount_amount }}</p>
        <p><strong>Tax ({{ tax_percent }}%):</strong> {{ tax_amount }}</p>
        <p><strong>Shipping:</strong> {{ shipping_charge }}</p>
        <p><strong>Grand Total:</strong> {{ final_total }}</p>
    </div>

    <div class="terms">
        <h4>Terms & Conditions</h4>
        <p>{{ quotation.terms|linebreaks }}</p>
    </div>

    <div class="signature">
        <p>For {{ company.name }}</p>
        <p><strong>Authorised Signatory</strong></p>
        {% if signature_b64 %}
            <img src="{{ signature_b64 }}" style="height:60px;">
        {% elif company.signature %}
            <img src="{{ base_url }}{{ company.signature.url }}" style="height:60px;">
        {% else %}
            <p style="font-style:italic;">(Signature)</p>
        {% endif %}
    </div>

    <div class="footer">
        <p>{{ company.name }} - {{ company.address }} - {{ company.phone }} - {{ company.email }}</p>
    </div>

</body>
</html>
'''