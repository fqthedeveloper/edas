from django.db import models
from companies.models import Company

class DropdownList(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    items = models.JSONField(default=list)  # list of strings

    def __str__(self):
        return self.name