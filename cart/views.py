from django.shortcuts import render
from products.models import HennaProduct

def view_cart(request):
    """Get to return shopping cart"""

    return render(request, 'cart/cart.html')