from django.http import HttpResponse
from .models import Order, OrderItem, Delivery
from products.models import HennaProduct
import json
import time
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """Handle a generic/unknown/unexpected webhook event"""
        return HttpResponse(content=f'Unhandled webhook received: {event["type"]}', status=200)

    def handle_payment_intent_succeeded(self, event):
        """Handle the payment_intent.succeeded webhook from Stripe"""
        intent = event.data.object
        pid = intent.id

        # Check if metadata exists and get the cart and save_info
        metadata = intent.get('metadata', {})
        cart = metadata.get('cart', None)
        save_info = metadata.get('save_info', False)
        delivery_method_id = metadata.get('delivery_method_id', None)

        if not cart:
            logger.error('Cart information is missing from the PaymentIntent metadata')
            return HttpResponse(content=f'Webhook received: {event["type"]} | ERROR: Cart metadata missing', status=400)

        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total_with_vat = round(intent.charges.data[0].amount / 100, 2)

        # Clean data in the shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # Get delivery cost based on delivery method ID
        delivery_cost = self.get_delivery_cost(delivery_method_id)

        # Check if the order already exists
        order_exists = self.check_order_exists(shipping_details, billing_details, cart, pid, grand_total_with_vat)

        if order_exists:
            return HttpResponse(content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database', status=200)

        # Create the order if it doesn't exist
        order = self.create_order(shipping_details, billing_details, cart, pid, delivery_cost)
        if not order:
            return HttpResponse(content=f'Webhook received: {event["type"]} | ERROR: Order creation failed', status=500)

        return HttpResponse(content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook', status=200)

    def get_delivery_cost(self, delivery_method_id):
        """Retrieve delivery cost based on delivery method ID"""
        if delivery_method_id is None:
            logger.error('No delivery method ID provided')
            return Decimal('0.00')

        try:
            delivery_method = Delivery.objects.get(id=delivery_method_id)
            return Decimal(delivery_method.cost)
        except Delivery.DoesNotExist:
            logger.error(f'Delivery method not found: {delivery_method_id}')
            return Decimal('0.00')

    def check_order_exists(self, shipping_details, billing_details, cart, pid, grand_total_with_vat):
        """Check if an order already exists in the database"""
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total_with_vat,
                    original_cart=cart,
                    stripe_pid=pid,
                )
                return True
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        return False

    def create_order(self, shipping_details, billing_details, cart, pid, delivery_cost):
        """Create a new order in the database"""
        try:
            order = Order.objects.create(
                full_name=shipping_details.name,
                email=billing_details.email,
                phone_number=shipping_details.phone,
                street_address1=shipping_details.address.line1,
                street_address2=shipping_details.address.line2,
                town_or_city=shipping_details.address.city,
                postcode=shipping_details.address.postal_code,
                county=shipping_details.address.state,
                country=shipping_details.address.country,
                original_cart=cart,
                stripe_pid=pid,
                delivery_cost=delivery_cost,
            )
            for item_id, item_data in json.loads(cart).items():
                product = HennaProduct.objects.get(id=item_id)
                order_line_item = OrderItem(
                    order=order,
                    product=product,
                    quantity=item_data,
                )
                order_line_item.save()
            return order
        except Exception as e:
            logger.error(f'Error creating order: {e}')
            return None

    def handle_payment_intent_payment_failed(self, event):
        """Handle the payment_intent.payment_failed webhook from Stripe"""
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200)
