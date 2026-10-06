import logging
import base64
import io
import os
from django.core.files.base import ContentFile
from django.template import Template as DjangoTemplate, Context
from django.conf import settings
from background_task import background
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from .models import Document, DocumentValue
from .services import (
    generate_pdf_from_html,
    generate_qr_code,
    image_to_base64,
)
from sequences.services import mark_number_used

logger = logging.getLogger(__name__)


# ---- Core Generation Logic (used by both sync and async) ----
def _generate_document(doc):
    """
    Core document generation logic.
    Returns True on success, False on failure.
    """
    logger.info(f"Generating document: {doc.document_number}")

    # Build context
    context = {}
    for val in doc.values.all():
        context[val.field.field_name] = val.value

    company = doc.client.company
    context['company'] = company
    context['document'] = doc
    context['base_url'] = getattr(settings, 'BASE_URL', 'http://localhost:8000')

    # --- Convert images to base64 for PDF rendering ---
    logo_b64 = None
    if company.logo:
        logo_b64 = image_to_base64(company.logo)
        if logo_b64:
            context['logo_b64'] = logo_b64

    if company.signature:
        signature_b64 = image_to_base64(company.signature)
        if signature_b64:
            context['signature_b64'] = signature_b64

    if logo_b64:
        context['watermark_b64'] = logo_b64
        context['has_watermark'] = True
    else:
        context['has_watermark'] = False

    # --- Generate QR code (for both PDF and DOCX) ---
    try:
        qr_data = f"{context['base_url']}/documents/verify/{doc.document_number}"
        qr_bytes = generate_qr_code(qr_data)  # returns raw PNG bytes
        # Save QR to model (optional)
        doc.qr_code.save(f"{doc.document_number}_qr.png", ContentFile(qr_bytes), save=False)
        # For PDF: embed as base64
        if doc.qr_code:
            qr_b64 = image_to_base64(doc.qr_code)
            if qr_b64:
                context['qr_b64'] = qr_b64
        # For DOCX: we need an InlineImage (will be created later)
        qr_bytes_io = io.BytesIO(qr_bytes)   # BytesIO object for InlineImage
    except Exception as e:
        logger.error(f"QR code generation failed: {e}")
        return False

    # ---- Generate PDF ----
    try:
        html_string = DjangoTemplate(doc.template.html_layout).render(Context(context))
        pdf_bytes = generate_pdf_from_html(html_string, base_url=context.get('base_url'))
        doc.generated_pdf.save(f"{doc.document_number}.pdf", ContentFile(pdf_bytes), save=False)
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        return False

    # ---- Generate DOCX with embedded QR ----
    try:
        # Load the Word template
        docx_template = DocxTemplate(doc.template.docx_template.path)

        # Convert QR bytes to InlineImage (adjust width/height as needed)
        qr_image = InlineImage(docx_template, qr_bytes_io, width=Mm(25), height=Mm(25))
        context['qr_code'] = qr_image   # Must match the placeholder in your .docx template

        # Render template with all context (including qr_code)
        docx_template.render(context)

        # Save to bytes
        docx_output = io.BytesIO()
        docx_template.save(docx_output)
        docx_bytes = docx_output.getvalue()

        # Save to model
        doc.generated_docx.save(f"{doc.document_number}.docx", ContentFile(docx_bytes), save=False)
    except Exception as e:
        logger.error(f"DOCX generation failed: {e}")
        return False

    # Mark document as generated
    doc.status = 'generated'
    doc.save()

    # Mark number as used (for sequence)
    prefix = doc.document_number.rsplit('/', 1)[0] + '/'
    try:
        number = int(doc.document_number.rsplit('/', 1)[1])
        mark_number_used(prefix, number)
    except Exception as e:
        logger.warning(f"Could not mark number as used: {e}")

    logger.info(f"Document {doc.document_number} generated successfully.")
    return True


# ---- Background Task (kept for backward compatibility) ----
@background(schedule=0)
def generate_document_pdf_docx(document_id):
    """
    Background task version – schedules the generation.
    """
    logger.info(f"Starting background task for document ID: {document_id}")

    try:
        doc = Document.objects.get(id=document_id)
    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found.")
        return

    doc.status = 'processing'
    doc.save()

    success = _generate_document(doc)
    if not success:
        doc.status = 'failed'
        doc.save()