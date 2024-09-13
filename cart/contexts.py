from django.conf import settings
from django.shortcuts import get_object_or_404
from decimal import Decimal, ROUND_HALF_UP
from products.models import HennaProduct

def cart_contents(request):
    """Retrieve the contents of the cart and calculate totals without delivery costs"""

    cart_items = []
    total = Decimal('0.00')
    product_count = 0
    cart = request.session.get('cart', {})

    for item_id, item_data in cart.items():
        quantity = item_data.get('quantity', 1)
        product = get_object_or_404(HennaProduct, pk=item_id)
        discounted_price = Decimal(item_data.get('discounted_price', '0.00'))  # Discounted price is Decimal
        total += quantity * discounted_price
        product_count += quantity
        cart_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'product': product,
            'discounted_price': discounted_price,
        })

    # Round all monetary values to 2 decimal places
    # https://docs.python.org/3/library/decimal.html#decimal.Decimal.quantize
    total = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    grand_total = total

    # Prepare context dictionary
    context = {
        'cart_items': cart_items,
        'total': total,
        'product_count': product_count,
        'grand_total': grand_total,
    }

    return context
