from django.contrib import admin
from .models import Template, TemplateField
# Register your models here.

admin.site.register(Template)
admin.site.register(TemplateField)