from .models import AuditLog
from django.utils.timezone import now

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            AuditLog.objects.create(
                user=request.user,
                action=request.path,
                ip_address=request.META.get('REMOTE_ADDR'),
                details={'method': request.method}
            )
        return response