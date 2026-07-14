from django.urls import path
from . import views

urlpatterns = [
    # Template management
    path('', views.TemplateListView.as_view(), name='template_list'),
    path('add/', views.TemplateCreateView.as_view(), name='template_add'),
    path('<int:pk>/edit/', views.TemplateUpdateView.as_view(), name='template_edit'),
    path('<int:pk>/delete/', views.TemplateDeleteView.as_view(), name='template_delete'),

    # Field management (nested under a specific template)
    path('<int:template_pk>/fields/', views.TemplateFieldListView.as_view(), name='template_field_list'),
    path('<int:template_pk>/fields/add/', views.TemplateFieldCreateView.as_view(), name='template_field_add'),
    path('field/<int:pk>/edit/', views.TemplateFieldUpdateView.as_view(), name='template_field_edit'),
    path('field/<int:pk>/delete/', views.TemplateFieldDeleteView.as_view(), name='template_field_delete'),
]