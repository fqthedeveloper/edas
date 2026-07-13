from django.db import models
from accounts.models import User

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    details = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"