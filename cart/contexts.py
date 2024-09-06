from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import HennaProduct

def cart_contents(request):
    """ Retrieve the contents of the cart and calculate totals and delivery costs """

    cart_items = []
    total = Decimal('0.00')
    product_count = 0
    cart = request.session.get('cart', {})

    for item_id, quantity in cart.items():
        product = get_object_or_404(HennaProduct, pk=item_id)
        total += quantity * product.price
        product_count += quantity
        cart_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'product': product,
        })

    # Calculate delivery and free delivery delta
    if total < Decimal(settings.FREE_DELIVERY_THRESHOLD):
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE) / Decimal('100')
        free_delivery_delta = Decimal(settings.FREE_DELIVERY_THRESHOLD) - total
    else:
        delivery = Decimal('0.00')
        free_delivery_delta = Decimal('0.00')

    grand_total = delivery + total

    # Prepare context dictionary
    context = {
        'cart_items': cart_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': Decimal(settings.FREE_DELIVERY_THRESHOLD),
        'grand_total': grand_total,
    }

    return context
