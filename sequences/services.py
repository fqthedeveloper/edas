from .models import DocumentNumberSequence
from documents.models import Document

def get_next_number(prefix):
    seq, created = DocumentNumberSequence.objects.get_or_create(prefix=prefix)
    # collect used numbers from sequence and from existing documents
    used = set(seq.used_numbers)
    # also query documents with that prefix
    existing = Document.objects.filter(document_number__startswith=prefix)
    for doc in existing:
        try:
            num = int(doc.document_number.replace(prefix, ''))
            used.add(num)
        except:
            pass
    # start from last_number + 1
    candidate = seq.last_number + 1
    while candidate in used:
        candidate += 1
    seq.last_number = candidate
    seq.save()
    return candidate

def mark_number_used(prefix, number):
    seq, created = DocumentNumberSequence.objects.get_or_create(prefix=prefix)
    if number not in seq.used_numbers:
        seq.used_numbers.append(number)
        seq.save()