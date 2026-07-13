from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Client
from .forms import ClientForm

class ClientListView(ListView):
    model = Client
    template_name = 'clients/list.html'
    context_object_name = 'clients'

class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/form.html'
    success_url = reverse_lazy('client_list')

class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/form.html'
    success_url = reverse_lazy('client_list')

class ClientDeleteView(DeleteView):
    model = Client
    success_url = reverse_lazy('client_list')
    template_name = 'clients/confirm_delete.html'