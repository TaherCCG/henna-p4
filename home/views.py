from django.shortcuts import render
from products.models import HennaProduct

def index(request):
    """Get the top 3 most-rated products"""
    top_rated_products = HennaProduct.objects.filter(rating__isnull=False).order_by('-rating')[:6]
    
    context = {
        'products': top_rated_products,
    }
    return render(request, 'home/index.html', context)