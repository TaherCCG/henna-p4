from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
from django.http import JsonResponse
from .forms import OrderForm
from .models import Delivery, Order, OrderItem, HennaProduct
from cart.contexts import cart_contents
import stripe

def checkout(request):
    """
    Display the checkout form and calculate delivery costs based on the user's cart.
    Also handles form submission for order processing.
    """
    # Stripe configuration
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # Retrieve current cart data, including items and totals
    current_cart = cart_contents(request)
    cart = request.session.get('cart', {})

    # Redirect if the cart is empty
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')

    total_cost = current_cart['total']

    # Fetch active delivery methods
    delivery_methods = Delivery.objects.filter(active=True)
    free_delivery_threshold = Decimal(settings.FREE_DELIVERY_THRESHOLD)

    # Default delivery options
    delivery_cost = Decimal('0.00')
    delivery_name = 'Standard Delivery'

    # Determine delivery cost based on total cost
    if total_cost < free_delivery_threshold:
        standard_delivery = delivery_methods.filter(name='Standard Delivery').first()
        if standard_delivery:
            delivery_cost = standard_delivery.cost
            delivery_name = standard_delivery.name
    else:
        free_delivery = delivery_methods.filter(name='Free Delivery').first()
        if free_delivery:
            delivery_cost = Decimal('0.00')
            delivery_name = free_delivery.name

    # Calculate free delivery delta
    free_delivery_delta = free_delivery_threshold - total_cost if total_cost < free_delivery_threshold else Decimal('0.00')

    # Calculate totals
    delivery_cost = delivery_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    grand_total = (total_cost + delivery_cost).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    vat_rate = Decimal(settings.VAT_RATE)
    vat_amount = (total_cost * vat_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # Update grand total with VAT and delivery cost
    grand_total_with_vat = (grand_total + vat_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # Create a Stripe payment intent
    stripe.api_key = stripe_secret_key
    stripe_total = round(grand_total_with_vat * 100)
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    # Handle form submission
    if request.method == 'POST':
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST.get('street_address2', ''),
            'county': request.POST.get('county', ''),
        }

        order_form = OrderForm(form_data)

        # Use quantities from the cart rather than the form
        quantities = {}

        for item in current_cart['cart_items']:
            product_id = item['product'].id  # Access product ID from the cart item
            quantity = item['quantity']  # Use the quantity from the cart

            # Validate the cart's quantity
            if quantity <= 0:
                messages.error(request, f"Quantity for product ID {product_id} must be greater than 0.")
                return redirect('checkout')

            quantities[product_id] = quantity

        # Process the form if valid
        if order_form.is_valid():
            order = order_form.save(commit=False)

            # Get selected delivery method
            selected_delivery_method = request.POST.get('delivery_method')  # Assuming this is the field name in your form
            if selected_delivery_method:
                selected_delivery = Delivery.objects.get(id=selected_delivery_method)
                order.delivery_method = selected_delivery
                order.delivery_cost = selected_delivery.cost  # Use the selected delivery cost
            else:
                order.delivery_cost = delivery_cost  # Fallback to calculated delivery cost if none selected

            order.vat_amount = vat_amount
            order.grand_total_with_vat = (total_cost + order.delivery_cost + vat_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)  # Ensure correct total
            order.save()

            # Process cart items with validated quantities
            for product_id, quantity in quantities.items():
                try:
                    product = HennaProduct.objects.get(id=product_id)
                    order_item = OrderItem(
                        order=order,
                        product=product,
                        quantity=quantity,
                    )
                    order_item.save()
                except HennaProduct.DoesNotExist:
                    messages.error(request, f"One of the items in your cart wasn't found for product ID {product_id}.")
                    order.delete()  # Rollback the order if product is not found
                    return redirect(reverse('view_cart'))

            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            messages.error(request, "There was an issue with your form; please check your information.")

    else:
        order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(request, "Stripe public key is missing. Did you set it in your environment?")

    context = {
        'order_form': order_form,
        'total_cost': total_cost,
        'delivery_cost': delivery_cost,
        'grand_total': grand_total,
        'grand_total_with_vat': grand_total_with_vat,  # Ensure this reflects the correct amount
        'vat_amount': vat_amount,
        'delivery_name': delivery_name,
        'free_delivery_threshold': free_delivery_threshold,
        'is_threshold_met': total_cost >= free_delivery_threshold,
        'delivery_methods': delivery_methods,
        'free_delivery_delta': free_delivery_delta,
        'cart_items': current_cart['cart_items'], 
        'product_count': current_cart['product_count'], 
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, 'checkout/checkout.html', context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts and display the order confirmation.
    """
    save_info = request.session.get('save-info')
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, f'Order successfully processed! \
                    Your order number is {order_number}. \
                    A confirmation email will be sent to {order.email}.')
    
    # Clear the cart from the session if it exists
    if 'cart' in request.session:
        del request.session['cart']
    
    # Define the template and context for rendering
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)

def update_delivery(request, delivery_id):
    """
    Update the delivery cost and grand total when the user selects a different delivery method.
    Returns the updated values as JSON.
    """
    cart = request.session.get('cart', {})
    
    current_cart = cart_contents(request)
    total_cost = current_cart['total']
    
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
