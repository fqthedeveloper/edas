from celery import shared_task
from django.core.files.base import ContentFile
from django.template import Template as DjangoTemplate, Context
from django.conf import settings
from .models import Document, DocumentValue
from .services import generate_pdf_from_html, generate_docx_from_template, generate_qr_code, generate_barcode
from sequences.services import mark_number_used
import logging

logger = logging.getLogger(__name__)

@shared_task
def generate_document_pdf_docx(document_id):
    logger.info(f"Starting document generation for ID: {document_id}")
    
    doc = Document.objects.get(id=document_id)
    logger.info(f"Document: {doc.document_number}, Template: {doc.template.name}")
    
    # Build context from DocumentValue
    context = {}
    for val in doc.values.all():
        context[val.field.field_name] = val.value
        logger.info(f"Field: {val.field.field_name} = {val.value}")
    
    # Add company
    company = doc.client.company
    context['company'] = company
    context['document'] = doc
    
    # Log the complete context for debugging
    logger.info(f"Context keys: {list(context.keys())}")
    
    # Generate QR code
    qr_data = f"{getattr(settings, 'BASE_URL', 'http://localhost:8000')}/verify/{doc.document_number}"
    qr_bytes = generate_qr_code(qr_data)
    doc.qr_code.save(f"{doc.document_number}_qr.png", ContentFile(qr_bytes), save=False)
    logger.info("QR code generated")
    
    # Generate Barcode
    barcode_bytes = generate_barcode(doc.document_number)
    doc.barcode.save(f"{doc.document_number}_barcode.png", ContentFile(barcode_bytes), save=False)
    logger.info("Barcode generated")
    
    # --- PDF Generation ---
    try:
        html_string = DjangoTemplate(doc.template.html_layout).render(Context(context))
        logger.info(f"HTML length: {len(html_string)} characters")
        
        pdf_bytes = generate_pdf_from_html(html_string)
        doc.generated_pdf.save(f"{doc.document_number}.pdf", ContentFile(pdf_bytes), save=False)
        logger.info("PDF generated successfully")
    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}")
        doc.status = 'failed'
        doc.save()
        raise
    
    # --- DOCX Generation ---
    try:
        docx_bytes = generate_docx_from_template(doc.template.docx_template.path, context)
        doc.generated_docx.save(f"{doc.document_number}.docx", ContentFile(docx_bytes), save=False)
        logger.info("DOCX generated successfully")
    except Exception as e:
        logger.error(f"DOCX generation failed: {str(e)}")
        doc.status = 'failed'
        doc.save()
        raise
    
    doc.status = 'generated'
    doc.save()
    
    # Mark number as used
    prefix = doc.document_number.rsplit('/', 1)[0] + '/'
    try:
        number = int(doc.document_number.rsplit('/', 1)[1])
        mark_number_used(prefix, number)
        logger.info(f"Number marked as used: {number}")
    except:
        pass
    
    logger.info(f"Document {doc.document_number} generation complete")