from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    gst = models.CharField(max_length=20, blank=True)
    pan = models.CharField(max_length=20, blank=True)
    address = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    stamp = models.ImageField(upload_to='stamps/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name