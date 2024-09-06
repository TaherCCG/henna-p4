from django.shortcuts import render, redirect
from products.models import HennaProduct

def view_cart(request):
    """Get to return shopping cart"""

    return render(request, 'cart/cart.html')


def add_to_cart(request, item_id):
    """ Add a quantity of the specified product to the shopping cart """

    quantity = int(request.POST.get('quantity', 1)) 
    redirect_url = request.POST.get('redirect_url')
    
    cart = request.session.setdefault('cart', {})
    
    cart[item_id] = cart.get(item_id, 0) + quantity

    request.session.modified = True
    
    return redirect(redirect_url)