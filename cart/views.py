from django.shortcuts import render, redirect
from products.models import HennaProduct

def view_cart(request):
    """Get to return shopping cart"""
    cart = request.session.get('cart', {})
    product_ids = cart.keys()
    products = HennaProduct.objects.filter(id__in=product_ids)
    
    cart_items = []
    total = 0
    for product in products:
        quantity = cart[str(product.id)]
        discounted_price = product.get_discounted_price()
        subtotal = discounted_price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'discounted_price': discounted_price,
            'subtotal': subtotal
        })
        total += subtotal
    
    delivery = 0
    grand_total = total + delivery
    free_delivery_threshold = 50
    free_delivery_delta = max(free_delivery_threshold - total, 0)

    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'delivery': delivery,
        'grand_total': grand_total,
        'free_delivery_delta': free_delivery_delta
    })

def add_to_cart(request, item_id):
    """Add a quantity of the specified product to the shopping cart"""
    quantity = int(request.POST.get('quantity', 1))
    redirect_url = request.POST.get('redirect_url', '/')
    
    cart = request.session.setdefault('cart', {})
    cart[item_id] = cart.get(item_id, 0) + quantity
    request.session.modified = True
    
    return redirect(redirect_url)
