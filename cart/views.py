from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal, ROUND_HALF_UP
from products.models import HennaProduct
from django.conf import settings

def view_cart(request):
    """Retrieve and display the shopping cart contents."""
    cart = request.session.get('cart', {})
    
    cart_items = []
    total = Decimal('0.00')
    
    for item_id, item_data in cart.items():
        quantity = item_data.get('quantity', 1)
        discounted_price = Decimal(item_data.get('discounted_price', '0.00'))
        product = get_object_or_404(HennaProduct, id=item_id)
        subtotal = quantity * discounted_price
        
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'discounted_price': discounted_price,
            'subtotal': subtotal
        })
        
        total += subtotal

    # Round the total to 2 decimal places
    # https://docs.python.org/3/library/decimal.html#decimal.Decimal.quantize
    total = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    grand_total = total

    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'grand_total': grand_total
    })


def add_to_cart(request, item_id):
    """Add a specified quantity of a product to the shopping cart with its discounted price."""
    quantity = int(request.POST.get('quantity', 1))
    redirect_url = request.POST.get('redirect_url', '/')
    
    cart = request.session.setdefault('cart', {})
    
    try:
        product = HennaProduct.objects.get(id=item_id)
    except HennaProduct.DoesNotExist:
        return redirect(redirect_url)
    
    discounted_price = product.get_discounted_price()
    
    discounted_price_str = str(discounted_price)
    
    if item_id in cart:
        cart[item_id]['quantity'] += quantity
    else:
        cart[item_id] = {
            'quantity': quantity,
            'discounted_price': discounted_price_str
        }
    
    request.session.modified = True
    
    return redirect(redirect_url)
