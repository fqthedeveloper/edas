import glob, pypdf, re, os, json, django, time
from django.db import connection, transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edas.settings')
django.setup()

from companies.models import Company
from clients.models import Client
from products.models import Product
from templatesapp.models import Template, TemplateField
from documents.models import Document, DocumentValue
from accounts.models import User
from sequences.models import DocumentNumberSequence

# Set sqlite timeout to 60 seconds to avoid locking errors
with connection.cursor() as cursor:
    cursor.execute("PRAGMA busy_timeout = 60000;")

admin_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
company = Company.objects.first()
template = Template.objects.first()
template_fields = {f.field_name: f for f in template.fields.all()}

def parse_full_pdf(path):
    try:
        reader = pypdf.PdfReader(path)
        if len(reader.pages) == 0: return None
        text = reader.pages[0].extract_text()
    except Exception:
        return None

    data = {}
    
    # 1. Header fields
    m = re.search(r'TC NO:\s*([^\s]+)\s+DATE:\s*([^\s\n\r]+)', text)
    if m:
        data['tc_number'] = m.group(1).strip()
        data['date'] = m.group(2).strip()
        
    m = re.search(r'CLIENT NAME:\s*([^\n\r]+)', text)
    if m:
        data['client_name'] = m.group(1).strip()
        
    m = re.search(r'CLIENT PO NO:\s*([^\n\r]+?)\s+PO DATE:\s*([^\s\n\r]+)', text)
    if m:
        data['client_po_no'] = m.group(1).strip()
        data['po_date'] = m.group(2).strip()
        
    m = re.search(r'FILTER SERIAL NUMBER:\s*([^\n\r]+?)\s+TESTING DATE:\s*([^\s\n\r]+)', text)
    if m:
        data['filter_serial_number'] = m.group(1).strip()
        data['testing_date'] = m.group(2).strip()
        
    m = re.search(r'EQUIPMENT USED FOR TESTING:\s*([^\n\r]+)', text)
    if m:
        data['equipment_used'] = m.group(1).strip()
        
    m = re.search(r'TYPE OF FILTER\s*:\s*([^\n\r]+)', text)
    if m:
        data['filter_type'] = m.group(1).strip()

    # 2. TEST RESULT block:
    m = re.search(r'INITIAL PRESSURE DROP \(Pa\)\s+EFFICIENCY\s+FILTER CLASS\s*\n\s*(.+?)\s+TEST TYPE\s*:\s*([^\n\r]+)', text, re.DOTALL)
    if m:
        res_line = m.group(1).strip().replace('\n', ' ')
        data['test_type'] = m.group(2).strip()
        m_fc = re.search(r'(EU\s*\d+|H\d+|U\d+)\s*$', res_line, re.IGNORECASE)
        if m_fc:
            data['filter_class'] = m_fc.group(1).strip()
            rest = res_line[:m_fc.start()].strip()
        else:
            data['filter_class'] = ''
            rest = res_line
            
        m_id = re.match(r'^(.*?(?:%|Pa))\s+(.*)$', rest)
        if m_id:
            data['test_initial_pressure_drop'] = m_id.group(1).strip()
            data['efficiency'] = m_id.group(2).strip()
        else:
            data['test_initial_pressure_drop'] = rest
            data['efficiency'] = ''

    # 3. TEST DATA block:
    m = re.search(r'TEST AIRFLOW\s+AIR VELOCITY\s+AIR\s*(?:TEMPERATURE)?\s*\n\s*(?:TEMPERATURE\s*\n)?\s*(.+?)\s*TEST RESULT', text, re.DOTALL)
    if m:
        td_line = m.group(1).strip().replace('\n', ' ')
        m_td = re.search(r'^(.*?CFM)\s+(.*?FPM)\s+(.*)$', td_line, re.IGNORECASE)
        if m_td:
            data['test_airflow'] = m_td.group(1).strip()
            data['air_velocity'] = m_td.group(2).strip()
            data['air_temperature'] = m_td.group(3).strip()
        else:
            data['test_airflow'] = td_line
            
    # 4. PRODUCT DETAILS bottom row:
    m = re.search(r'TEMPERATURE\s*\n\s*(\d+\s*CFM)\s+(.+?)\s+(\d+\s*(?:Pa|PA))\s+([A-Za-z]+)\s*TEST DATA', text, re.DOTALL)
    if m:
        data['air_flow_rate'] = m.group(1).strip()
        data['initial_pressure_drop'] = m.group(2).strip().replace('\n', ' ')
        data['final_pressure_drop'] = m.group(3).strip()
        data['temperature'] = m.group(4).strip()
        
    # 5. PRODUCT DETAILS top row:
    m = re.search(r'MOC\s*\n\s*(.+?)\s*AIR FLOW RATE', text, re.DOTALL)
    if m:
        top_str = m.group(1).strip().replace('\n', ' ')
        m_top = re.search(r'^(.*?)\s+(\d+\s*CFM)\s+(\d+\s*X\s*\d+\s*X\s*\d+\s*MM)\s+(.+)$', top_str, re.IGNORECASE)
        if m_top:
            data['filter_media'] = m_top.group(1).strip()
            data['filter_capacity'] = m_top.group(2).strip()
            data['filter_dimension'] = m_top.group(3).strip()
            data['moc'] = m_top.group(4).strip()
        else:
            data['filter_media'] = top_str

    return data

pdf_candidates = []
for p in glob.glob('d:/FQ/Django/EDAS Project/**/*.pdf', recursive=True):
    fname = os.path.basename(p).lower()
    if 'debug' in fname or 'test' in fname or 'preview' in fname:
        continue
    pdf_candidates.append(p)

print('Indexing unique PDFs by TC Number...')
unique_pdf_map = {}
for p in pdf_candidates:
    data = parse_full_pdf(p)
    if data and data.get('tc_number'):
        tc = data['tc_number']
        if tc not in unique_pdf_map:
            unique_pdf_map[tc] = (p, data)

print(f'Total distinct certificates to process: {len(unique_pdf_map)}')

clients_cache = {c.name.strip().lower(): c for c in Client.objects.all()}
products_cache = {p.name.strip().lower(): p for p in Product.objects.all()}
existing_docs = {d.document_number: d for d in Document.objects.all()}

created_count = 0
updated_count = 0
used_numbers = []

for tc_number, (path, data) in sorted(unique_pdf_map.items()):
    client_name = data.get('client_name', 'Unknown Client').strip()
    filter_type = data.get('filter_type', 'Air Filter').strip()
    
    try:
        num = int(tc_number.split('/')[-1])
        used_numbers.append(num)
    except Exception:
        pass

    # Client
    c_key = client_name.lower()
    if c_key in clients_cache:
        client = clients_cache[c_key]
    else:
        client = Client.objects.create(
            company=company,
            name=client_name,
            default_template=template
        )
        clients_cache[c_key] = client

    # Product
    p_key = filter_type.lower()
    if p_key in products_cache:
        product = products_cache[p_key]
    else:
        product = Product.objects.create(
            company=company,
            name=filter_type,
            default_template=template
        )
        products_cache[p_key] = product

    suffix = tc_number.split('/')[-1]
    rel_pdf_path = f'generated/pdf/AFPL/2026-27/{suffix}.pdf'
    rel_qr_path = f'generated/qr/AFPL/2026-27/{suffix}_qr.png'
    full_qr_path = os.path.join('media', rel_qr_path.replace('/', os.sep))
    has_qr = os.path.exists(full_qr_path)
    
    if tc_number in existing_docs:
        doc = existing_docs[tc_number]
        doc.client = client
        doc.product = product
        doc.template = template
        doc.status = 'generated'
        doc.form_data = data
        if has_qr:
            doc.qr_code = rel_qr_path
        doc.save()
        updated_count += 1
    else:
        doc = Document.objects.create(
            client=client,
            product=product,
            template=template,
            document_number=tc_number,
            created_by=admin_user,
            status='generated',
            generated_pdf=rel_pdf_path,
            qr_code=rel_qr_path if has_qr else '',
            form_data=data
        )
        existing_docs[tc_number] = doc
        created_count += 1

        # Bulk create DocumentValues for this new document
        doc_values = []
        for fname, val in data.items():
            if fname in template_fields and val:
                doc_values.append(DocumentValue(
                    document=doc,
                    field=template_fields[fname],
                    value=str(val)
                ))
        if doc_values:
            DocumentValue.objects.bulk_create(doc_values, ignore_conflicts=True)

# Sequence update
if used_numbers:
    seq, _ = DocumentNumberSequence.objects.get_or_create(prefix='AFPL/2026-27/', defaults={'last_number': max(used_numbers)})
    seq.last_number = max(max(used_numbers), seq.last_number)
    seq.used_numbers = sorted(list(set(seq.used_numbers + used_numbers)))
    seq.save()

print(f'FINISHED! Processed all unique certificates.')
print(f'New Created: {created_count}, Updated: {updated_count}.')
print(f'Total UNIQUE Documents in DB: {Document.objects.count()}')
print(f'Total DocumentValues in DB: {DocumentValue.objects.count()}')
