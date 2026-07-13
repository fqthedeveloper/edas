from django.db import models

class DocumentNumberSequence(models.Model):
    prefix = models.CharField(max_length=50, unique=True)
    last_number = models.PositiveIntegerField(default=0)
    used_numbers = models.JSONField(default=list)  # list of integers

    def __str__(self):
        return self.prefix