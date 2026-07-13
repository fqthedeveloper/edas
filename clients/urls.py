from django.urls import path
from . import views

urlpatterns = [
    path('', views.ClientListView.as_view(), name='client_list'),
    path('add/', views.ClientCreateView.as_view(), name='client_add'),
    path('<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_edit'),
    path('<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),
]