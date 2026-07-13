from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from documents.views import dashboard, verify_document

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),  # home
    path('verify/<str:document_number>/', verify_document, name='verify'),
    path('accounts/', include('accounts.urls')),
    path('clients/', include('clients.urls')),
    path('products/', include('products.urls')),
    path('dropdowns/', include('dropdowns.urls')),
    path('templates/', include('templatesapp.urls')),
    path('documents/', include('documents.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)