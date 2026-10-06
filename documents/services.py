import io
import base64
import os
import qrcode
import barcode
from barcode.writer import ImageWriter
from django.template import Template, Context
from django.conf import settings
from docxtpl import DocxTemplate
from django.core.files.storage import default_storage
from django.conf import settings  # optional, only if using Django



def image_to_base64(image_field):
    """
    Convert a Django ImageField to base64 data URI.
    Returns None if image doesn't exist or can't be read.
    """
    if not image_field or not image_field.name:
        return None

    try:
        # Try to get the file path
        if hasattr(image_field, 'path') and os.path.exists(image_field.path):
            path = image_field.path
        else:
            return None

        with open(path, 'rb') as f:
            image_data = f.read()
            ext = path.split('.')[-1].lower()
            mime_type = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'svg': 'image/svg+xml'
            }.get(ext, 'image/png')
            b64 = base64.b64encode(image_data).decode('utf-8')
            return f"data:{mime_type};base64,{b64}"

    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to convert image to base64: {e}")
        return None

def generate_qr_code_bytes(data: str) -> io.BytesIO:
    """Generate QR code image as BytesIO."""
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    output = io.BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    return output

def generate_pdf_from_html(html_string, base_url=None):
    """Generate PDF from HTML string with optional base URL for images."""
    try:
        from weasyprint import HTML
        if base_url:
            return HTML(string=html_string, base_url=base_url).write_pdf()
        else:
            return HTML(string=html_string).write_pdf()
    except ImportError:
        import pdfkit
        options = {
            'page-size': 'A4',
            'orientation': 'Portrait',
            'margin-top': '10mm',
            'margin-bottom': '10mm',
            'margin-left': '10mm',
            'margin-right': '10mm',
        }
        return pdfkit.from_string(html_string, False, options=options)

def generate_docx_from_template(template_path: str, context: dict) -> bytes:

    # 1. Load the template
    doc = DocxTemplate(template_path)

    # 2. Generate QR code as BytesIO
    qr_data = context.get('qr_data', 'https://airfil.in/verify/default')
    qr_stream = generate_qr_code_bytes(qr_data)

    # 3. Embed the QR as an InlineImage (adjust width to fit your table)
    #    width=25mm is safe for a 4‑column table cell; you can change it.
    qr_inline = InlineImage(doc, qr_stream, width=Mm(25), height=Mm(25))

    # 4. Replace the placeholder with the InlineImage
    context['qr_code'] = qr_inline

    # 5. Render and save to BytesIO
    doc.render(context)
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output.read()

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    output = io.BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    return output.read()

def generate_barcode(code):
    barcode_class = barcode.get_barcode_class('code128')
    barcode_img = barcode_class(code, writer=ImageWriter())
    output = io.BytesIO()
    barcode_img.write(output)
    output.seek(0)
    return output.read()