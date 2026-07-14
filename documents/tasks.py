# documents/tasks.py
import logging
from django.core.files.base import ContentFile
from django.template import Template, Context
from django.conf import settings
from background_task import background
from .models import Document, DocumentValue
from .services import (
    generate_pdf_from_html,
    generate_docx_from_template,
    generate_qr_code,
    generate_barcode
)
from sequences.services import mark_number_used

logger = logging.getLogger(__name__)

@background(schedule=0)  # 0 means run immediately
def generate_document_pdf_docx(document_id):
    """
    Background task to generate PDF and DOCX for a given document.
    """
    logger.info(f"Starting document generation for ID: {document_id}")

    try:
        doc = Document.objects.get(id=document_id)
    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found.")
        return

    logger.info(f"Document: {doc.document_number}, Template: {doc.template.name}")

    # Build context from DocumentValue
    context = {}
    for val in doc.values.all():
        context[val.field.field_name] = val.value
        logger.info(f"Field: {val.field.field_name} = {val.value}")

    # Add company and document
    company = doc.client.company
    context['company'] = company
    context['document'] = doc
    context['base_url'] = getattr(settings, 'BASE_URL', 'http://localhost:8000')

    logger.info(f"Context keys: {list(context.keys())}")

    # ---- Generate QR code ----
    qr_data = f"{context['base_url']}/verify/{doc.document_number}"
    try:
        qr_bytes = generate_qr_code(qr_data)
        doc.qr_code.save(f"{doc.document_number}_qr.png", ContentFile(qr_bytes), save=False)
        logger.info("QR code generated")
    except Exception as e:
        logger.error(f"QR code generation failed: {e}")
        doc.status = 'failed'
        doc.save()
        return

    # ---- Generate Barcode ----
    try:
        barcode_bytes = generate_barcode(doc.document_number)
        doc.barcode.save(f"{doc.document_number}_barcode.png", ContentFile(barcode_bytes), save=False)
        logger.info("Barcode generated")
    except Exception as e:
        logger.error(f"Barcode generation failed: {e}")
        doc.status = 'failed'
        doc.save()
        return

    # ---- Generate PDF ----
    try:
        html_string = Template(doc.template.html_layout).render(Context(context))
        logger.info(f"HTML length: {len(html_string)} characters")
        pdf_bytes = generate_pdf_from_html(html_string)
        doc.generated_pdf.save(f"{doc.document_number}.pdf", ContentFile(pdf_bytes), save=False)
        logger.info("PDF generated successfully")
    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}")
        doc.status = 'failed'
        doc.save()
        return

    # ---- Generate DOCX ----
    try:
        docx_bytes = generate_docx_from_template(doc.template.docx_template.path, context)
        doc.generated_docx.save(f"{doc.document_number}.docx", ContentFile(docx_bytes), save=False)
        logger.info("DOCX generated successfully")
    except Exception as e:
        logger.error(f"DOCX generation failed: {str(e)}")
        doc.status = 'failed'
        doc.save()
        return

    # ---- Update status ----
    doc.status = 'generated'
    doc.save()

    # Mark number as used
    prefix = doc.document_number.rsplit('/', 1)[0] + '/'
    try:
        number = int(doc.document_number.rsplit('/', 1)[1])
        mark_number_used(prefix, number)
        logger.info(f"Number marked as used: {number}")
    except Exception as e:
        logger.warning(f"Could not mark number as used: {e}")

    logger.info(f"Document {doc.document_number} generation complete")