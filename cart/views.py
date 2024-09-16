from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal, ROUND_HALF_UP
from products.models import HennaProduct
from django.http import JsonResponse
from django.conf import settings


def view_cart(request):
    """Retrieve and display the shopping cart contents and calculate totals."""
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

    free_delivery_threshold = Decimal(settings.FREE_DELIVERY_THRESHOLD)
    free_delivery_delta = free_delivery_threshold - total

    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'grand_total': grand_total,
        'free_delivery_delta': free_delivery_delta if free_delivery_delta > 0 else Decimal('0.00')
    })


def add_to_cart(request, item_id):
    """Add a specified quantity of a product to the shopping cart with its discounted price."""
    prduct = HennaProduct.objects.get(pk=item_id)
    quantity = int(request.POST.get('quantity', 1))
    redirect_url = request.POST.get('redirect_url', '/')

    cart = request.session.setdefault('cart', {})

    try:
        product = HennaProduct.objects.get(id=item_id)
    except HennaProduct.DoesNotExist:
        return redirect(redirect_url)

    discounted_price = product.get_discounted_price()
    str_item_id = str(item_id)

    if str_item_id in cart:
        cart[str_item_id]['quantity'] += quantity
    else:
        cart[str_item_id] = {
            'quantity': quantity,
            'discounted_price': str(discounted_price)
        }
        messages.success(request, f'Added {product.name} to your Shopping Cart' )

    request.session.modified = True

    return redirect(redirect_url)


def adjust_cart(request, item_id):
    """Adjust the quantity of a specific product in the cart."""
    if request.method != 'POST':
        return redirect('view_cart')

    quantity = int(request.POST.get('quantity', 0))
    str_item_id = str(item_id)
    cart = request.session.get('cart', {})

    if str_item_id in cart:
        if quantity > 0:
            cart[str_item_id]['quantity'] = quantity
        else:
            cart.pop(str_item_id)

    request.session['cart'] = cart

    return redirect('view_cart')


def remove_from_cart(request, item_id):
    """Remove a product from the shopping cart."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    str_item_id = str(item_id)
    cart = request.session.get('cart', {})

    if str_item_id in cart:
        cart.pop(str_item_id)
        request.session['cart'] = cart
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'error': 'Item not found in cart'}, status=404)

# Using session 
# https://docs.djangoproject.com/en/5.1/topics/http/sessions/