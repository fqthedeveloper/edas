import io
import qrcode
import barcode
from barcode.writer import ImageWriter
from django.template import Template, Context
from django.conf import settings
from docxtpl import DocxTemplate

def generate_pdf_from_html(html_string):
    """Generate PDF from HTML string using WeasyPrint"""
    try:
        from weasyprint import HTML
        return HTML(string=html_string).write_pdf()
    except ImportError:
        # Fallback to pdfkit if WeasyPrint is not available
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

def generate_docx_from_template(template_path, context):
    """Generate DOCX from template using docxtpl"""
    doc = DocxTemplate(template_path)
    doc.render(context)
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output.read()

def generate_qr_code(data):
    """Generate QR code image as bytes"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    output = io.BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    return output.read()

def generate_barcode(code):
    """Generate barcode image as bytes"""
    barcode_class = barcode.get_barcode_class('code128')
    barcode_img = barcode_class(code, writer=ImageWriter())
    output = io.BytesIO()
    barcode_img.write(output)
    output.seek(0)
    return output.read()