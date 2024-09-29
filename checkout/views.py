from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test

from profiles.forms import UserProfileForm
from .forms import OrderForm, DeliveryForm
from .models import Delivery, Order, OrderItem, HennaProduct, UserProfile 
from cart.contexts import cart_contents
from .utils import calculate_delivery_cost_and_totals
import stripe
import json


stripe_public_key = settings.STRIPE_PUBLIC_KEY
stripe_secret_key = settings.STRIPE_SECRET_KEY


@require_POST
def cache_checkout_data(request):
    """
    A view to handle the caching of checkout data before payment processing.
    Modifies the Stripe PaymentIntent to store cart and user metadata.
    """
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = stripe_secret_key
        stripe.PaymentIntent.modify(pid, metadata={
            'cart': json.dumps(request.session.get('cart', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


def checkout(request):
    """
    Display the checkout form and calculate delivery costs based on the user's cart.
    Handles form submission for order processing, including Stripe payment integration.
    """
    current_cart = cart_contents(request)
    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')

    calculations = calculate_delivery_cost_and_totals(current_cart['total'])
    stripe.api_key = stripe_secret_key
    stripe_total = round(calculations['grand_total_with_vat'] * 100)
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

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

        if order_form.is_valid():
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_cart = json.dumps(cart)
            order.save()

            # Save user profile info if save_info is checked
            if request.POST.get('save_info') and request.user.is_authenticated:
                profile = UserProfile.objects.get(user=request.user)
                profile.default_phone_number = request.POST.get('phone_number', profile.default_phone_number)
                profile.default_country = request.POST.get('country', profile.default_country)
                profile.default_postcode = request.POST.get('postcode', profile.default_postcode)
                profile.default_town_or_city = request.POST.get('town_or_city', profile.default_town_or_city)
                profile.default_street_address1 = request.POST.get('street_address1', profile.default_street_address1)
                profile.default_street_address2 = request.POST.get('street_address2', profile.default_street_address2)
                profile.default_county = request.POST.get('county', profile.default_county)
                profile.save()

            for item in current_cart['cart_items']:
                try:
                    product = HennaProduct.objects.get(id=item['product'].id)
                    order_item = OrderItem(
                        order=order,
                        product=product,
                        quantity=item['quantity'],
                    )
                    order_item.save()
                except HennaProduct.DoesNotExist:
                    messages.error(request, "One of the items in your cart wasn't found.")
                    order.delete()
                    return redirect('view_cart')

            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            messages.error(request, "There was an issue with your form; please check your information.")
    else:
        order_form_data = {}
        if request.user.is_authenticated:
            profile = UserProfile.objects.get(user=request.user)
            order_form_data = {
                'full_name': request.user.get_full_name(),
                'email': request.user.email,
                'phone_number': profile.default_phone_number,
                'country': profile.default_country,
                'postcode': profile.default_postcode,
                'town_or_city': profile.default_town_or_city,
                'street_address1': profile.default_street_address1,
                'street_address2': profile.default_street_address2,
                'county': profile.default_county,
            }
        order_form = OrderForm(initial=order_form_data)

    if not stripe_public_key:
        messages.warning(request, "Stripe public key is missing.")

    context = {
        'order_form': order_form,
        'total_cost': current_cart['total'],
        'delivery_cost': calculations['delivery_cost'],
        'grand_total': calculations['grand_total'],
        'grand_total_with_vat': calculations['grand_total_with_vat'],
        'vat_amount': calculations['vat_amount'],
        'delivery_name': calculations['delivery_name'],
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'is_threshold_met': current_cart['total'] >= settings.FREE_DELIVERY_THRESHOLD,
        'delivery_methods': Delivery.objects.filter(active=True),
        'free_delivery_delta': calculations['free_delivery_delta'],
        'cart_items': current_cart['cart_items'],
        'product_count': current_cart['product_count'],
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, 'checkout/checkout.html', context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts by displaying order confirmation and sending a confirmation email.
    Updates user profile if 'save_info' is selected.
    """
    save_info = request.session.get('save-info')
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        order.user_profile = profile
        order.save()

        if save_info:
            profile.default_phone_number = order.phone_number
            profile.default_country = order.country
            profile.default_postcode = order.postcode
            profile.default_town_or_city = order.town_or_city
            profile.default_street_address1 = order.street_address1
            profile.default_street_address2 = order.street_address2
            profile.default_county = order.county
            profile.save()

    subject = f'Order Confirmation: {order_number}'
    html_message = render_to_string('checkout/order_confirmation_email.html', {'order': order})
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = order.email

    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

    messages.success(request, 
                     f'Order successfully processed! Your order number is {order_number}. '
                     'A confirmation email has been sent to your email address.')

    if 'cart' in request.session:
        del request.session['cart']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)


def update_delivery(request, delivery_id):
    """
    Update the delivery cost and grand total when the user selects a different delivery method.
    """
    cart = request.session.get('cart', {})
    current_cart = cart_contents(request)
    total_cost = current_cart['total']
    
    try:
        selected_delivery = Delivery.objects.get(id=delivery_id)
        delivery_cost = selected_delivery.cost
    except Delivery.DoesNotExist:
        delivery_cost = Decimal('0.00')

    calculations = calculate_delivery_cost_and_totals(total_cost + delivery_cost)

    return JsonResponse({
        'delivery_cost': float(delivery_cost),
        'grand_total': float(calculations['grand_total']),
        'grand_total_with_vat': float(calculations['grand_total_with_vat']),
        'estimated_delivery_time': selected_delivery.estimated_delivery_time,
        'company_name': selected_delivery.company_name,
        'delivery_name': selected_delivery.name,
        'vat_amount': float(calculations['vat_amount'])
    })


# Helper function to check if the user is a superuser
def superuser_required(user):
    return user.is_superuser


@login_required
@user_passes_test(superuser_required)
def add_delivery(request):
    """
    Add a new delivery method through the delivery form.
    Handles form submission for adding delivery methods.
    """
    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Delivery method added successfully!")
            return redirect('list_deliveries')
    else:
        form = DeliveryForm()

    context = {
        'form': form,
        'title': 'Add Delivery Method',
        'edit_mode': False,
    }
    return render(request, 'checkout/delivery_form.html', context)


@login_required
@user_passes_test(superuser_required)
def edit_delivery(request, delivery_id):
    """
    Handles form submission for updating delivery methods.
    """
    delivery = get_object_or_404(Delivery, id=delivery_id)
    if request.method == 'POST':
        form = DeliveryForm(request.POST, instance=delivery)
        if form.is_valid():
            form.save()
            messages.success(request, "Delivery method updated successfully!")
            return redirect('list_deliveries')
    else:
        form = DeliveryForm(instance=delivery)

    context = {
        'form': form,
        'title': 'Edit Delivery Method',
        'edit_mode': True,
        'delivery': delivery,
    }
    return render(request, 'checkout/delivery_form.html', context)


@login_required
@user_passes_test(superuser_required)
@require_POST
def delete_delivery(request, delivery_id):
    """
    Handles form submission for deleting delivery methods.
    """
    delivery = get_object_or_404(Delivery, id=delivery_id)

    if request.method == 'POST':
        delivery.delete()
        messages.success(request, "Delivery method deleted successfully!")
        return redirect('list_deliveries')

    return HttpResponse(status=405)


@login_required
@user_passes_test(superuser_required)
def list_deliveries(request):
    """
    List all available delivery methods.
    """
    deliveries = Delivery.objects.all()
    context = {
        'deliveries': deliveries,
    }
    return render(request, 'checkout/list_deliveries.html', context)
