from django.urls import path
from . import views

urlpatterns = [
    path('', views.quotation_list, name='quotation_list'),
    path('create/', views.quotation_create, name='quotation_create'),
    path('<int:pk>/edit-items/', views.quotation_edit_items, name='quotation_edit_items'),
    path('<int:pk>/', views.quotation_detail, name='quotation_detail'),
    path('<int:pk>/pdf/', views.quotation_pdf, name='quotation_pdf'),
]