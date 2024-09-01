from django.shortcuts import render
from .models import HennaProduct

# Create your views here.

def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = HennaProduct.objects.all()

    context = {
        'products': products,
    }

    return render(request, 'products/products.html', context)