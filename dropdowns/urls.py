from django.urls import path
from . import views

urlpatterns = [
    path('', views.DropdownListView.as_view(), name='dropdown_list'),
    path('add/', views.DropdownCreateView.as_view(), name='dropdown_add'),
    path('<int:pk>/edit/', views.DropdownUpdateView.as_view(), name='dropdown_edit'),
    path('<int:pk>/delete/', views.DropdownDeleteView.as_view(), name='dropdown_delete'),
]