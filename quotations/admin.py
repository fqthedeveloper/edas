from django.contrib import admin
from .models import Quotation, QuotationItem

class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['quotation_number', 'client', 'date', 'status', 'grand_total']
    list_filter = ['status', 'date']
    search_fields = ['quotation_number', 'client__name']
    inlines = [QuotationItemInline]