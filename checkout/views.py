from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
from .forms import OrderForm
from django.http import JsonResponse
from .models import Delivery, Order
from cart.contexts import cart_contents

def checkout(request):
    """
    Display the checkout form and calculate delivery costs based on the user's cart.
    """
    # Use cart_contents function to get cart data and totals
    cart_context = cart_contents(request)
    cart = request.session.get('cart', {})
    
    # Redirect if the cart is empty
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')
    
    # Calculate total cost of items in the cart
    total_cost = cart_context['total']
    
    # Fetch delivery methods that are currently active
    delivery_methods = Delivery.objects.filter(active=True)
    free_delivery_threshold = Decimal(settings.FREE_DELIVERY_THRESHOLD)
    
    # Set default delivery options: Standard Delivery, unless the free delivery threshold is met
    delivery_cost = Decimal('0.00')
    delivery_name = 'Standard Delivery'
    
    # If total cost is below the threshold, apply Standard Delivery cost
    if total_cost < free_delivery_threshold:
        standard_delivery = delivery_methods.filter(name='Standard Delivery').first()
        if standard_delivery:
            delivery_cost = standard_delivery.cost
            delivery_name = standard_delivery.name
    else:
        # If threshold is met, apply Free Delivery
        free_delivery = delivery_methods.filter(name='Free Delivery').first()
        if free_delivery:
            delivery_cost = Decimal('0.00')
            delivery_name = free_delivery.name

    # Calculate free delivery delta
    free_delivery_delta = free_delivery_threshold - total_cost if total_cost < free_delivery_threshold else Decimal('0.00')

    # Round the delivery cost
    delivery_cost = delivery_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Calculate the grand total (total cost + delivery cost)
    grand_total = total_cost + delivery_cost
    grand_total = grand_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Calculate VAT
    vat_rate = Decimal(settings.VAT_RATE)
    vat_amount = total_cost * vat_rate
    vat_amount = vat_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # Calculate the grand total including VAT
    grand_total_with_vat = grand_total + vat_amount
    grand_total_with_vat = grand_total_with_vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Pass total cost and VAT to the order form for display
    order_form = OrderForm(total_cost=total_cost, vat_amount=vat_amount)

    context = {
        'order_form': order_form,
        'total_cost': total_cost,
        'delivery_cost': delivery_cost,
        'grand_total': grand_total,
        'grand_total_with_vat': grand_total_with_vat,
        'vat_amount': vat_amount,
        'delivery_name': delivery_name,
        'free_delivery_threshold': free_delivery_threshold,
        'is_threshold_met': total_cost >= free_delivery_threshold,
        'delivery_methods': delivery_methods,
        'free_delivery_delta': free_delivery_delta,
        'cart_items': cart_context['cart_items'],  # Add cart items to context
        'product_count': cart_context['product_count'],  # Add product count to context
    }
    
    return render(request, 'checkout/checkout.html', context)

def update_delivery(request, delivery_id):
    """
    Update the delivery cost and grand total when the user selects a different delivery method.
    """
    cart = request.session.get('cart', {})
    
    # Use cart_contents function to get cart data and totals
    cart_context = cart_contents(request)
    total_cost = cart_context['total']
    
    # Calculate VAT
    vat_rate = Decimal(settings.VAT_RATE)
    vat_amount = total_cost * vat_rate
    vat_amount = vat_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    try:
        # Fetch the selected delivery method from the database
        selected_delivery = Delivery.objects.get(id=delivery_id)
        delivery_cost = selected_delivery.cost
        estimated_delivery_time = selected_delivery.estimated_delivery_time
        company_name = selected_delivery.company_name
        delivery_type = selected_delivery.name
    except Delivery.DoesNotExist:
        # If the delivery method doesn't exist, set default values
        delivery_cost = Decimal('0.00')
        estimated_delivery_time = 'Not Available'
        company_name = 'Unknown'
        delivery_type = 'Unknown'

    # Calculate the grand total (total cost + selected delivery cost)
    grand_total = total_cost + delivery_cost
    grand_total = grand_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # Calculate the grand total including VAT
    grand_total_with_vat = grand_total + vat_amount
    grand_total_with_vat = grand_total_with_vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # Return the delivery cost, grand total, and other information as JSON
    return JsonResponse({
        'delivery_cost': float(delivery_cost),
        'grand_total': float(grand_total),
        'grand_total_with_vat': float(grand_total_with_vat),
        'estimated_delivery_time': estimated_delivery_time,
        'company_name': company_name,
        'delivery_name': delivery_type,
        'vat_amount': float(vat_amount)
    })
