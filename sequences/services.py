from .models import DocumentNumberSequence
from documents.models import Document

def get_next_number(prefix):
    seq, created = DocumentNumberSequence.objects.get_or_create(prefix=prefix)
    
    # Get all used numbers from the sequence's used_numbers list
    used = set(seq.used_numbers)
    
    # Also check existing documents in the database
    existing = Document.objects.filter(document_number__startswith=prefix)
    for doc in existing:
        try:
            num = int(doc.document_number.replace(prefix, ''))
            used.add(num)
        except:
            pass
    
    # Start from last_number + 1
    candidate = seq.last_number + 1
    
    # Find the next unused number
    while candidate in used:
        candidate += 1
    
    # Update the sequence
    seq.last_number = candidate
    seq.save()
    
    # Important: Mark this number as used immediately to prevent duplicates
    if candidate not in seq.used_numbers:
        seq.used_numbers.append(candidate)
        seq.save()
    
    return candidate

def mark_number_used(prefix, number):
    seq, created = DocumentNumberSequence.objects.get_or_create(prefix=prefix)
    if number not in seq.used_numbers:
        seq.used_numbers.append(number)
        seq.save()
        # Also update last_number if this number is higher
        if number > seq.last_number:
            seq.last_number = number
            seq.save()