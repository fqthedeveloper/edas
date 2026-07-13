from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Product
from .forms import ProductForm

class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('product_list')

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('product_list')

class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('product_list')
    template_name = 'products/confirm_delete.html'