from .models import Company

def company_processor(request):
    company = Company.objects.first()
    return {'company': company}