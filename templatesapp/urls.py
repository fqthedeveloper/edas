from django.urls import path
from . import views

urlpatterns = [
    path('', views.TemplateListView.as_view(), name='template_list'),
    path('add/', views.TemplateCreateView.as_view(), name='template_add'),
    path('<int:pk>/edit/', views.TemplateUpdateView.as_view(), name='template_edit'),
    path('<int:pk>/delete/', views.TemplateDeleteView.as_view(), name='template_delete'),
]