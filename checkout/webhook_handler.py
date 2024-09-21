from django.http import HttpResponse
from django.conf import settings
from decimal import Decimal
import json
import time
import stripe
import logging

from .models import Order, OrderItem, Delivery
from products.models import HennaProduct
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """Handle a generic/unknown/unexpected webhook event"""
        logger.info(f'Unhandled webhook received: {event["type"]}')
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200
        )

    async def handle_payment_intent_succeeded(self, event):
        """Handle the payment_intent.succeeded webhook from Stripe"""
        intent = event['data']['object']
        pid = intent['id']
        cart = intent['metadata']['cart']
        save_info = intent['metadata'].get('save_info', False)

        # Log for debugging
        logger.info(f'Payment Intent: {pid}')
        logger.info(f'Cart data: {cart}')

        # Retrieve Stripe charge asynchronously
        try:
            stripe_charge = await sync_to_async(stripe.Charge.retrieve)(intent['latest_charge'])
        except Exception as e:
            logger.error(f'Error retrieving charge from Stripe: {e}')
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: {e}',
                status=500
            )

        billing_details = stripe_charge['billing_details']
        shipping_details = intent['shipping']
        grand_total_with_vat = round(stripe_charge['amount'] / 100, 2)

        # Log for debugging
        logger.info(f'Billing details: {billing_details}')
        logger.info(f'Shipping details: {shipping_details}')

        # Clean data in the shipping details
        for field, value in shipping_details['address'].items():
            if value == "":
                shipping_details['address'][field] = None

        # Retrieve delivery method and cost from metadata
        delivery_method_id = intent['metadata']['delivery_method_id']
        try:
            delivery_method = Delivery.objects.get(id=delivery_method_id)
            delivery_cost = Decimal(delivery_method.cost)
        except Delivery.DoesNotExist:
            logger.error(f'Delivery method not found: {delivery_method_id}')
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: Delivery method not found',
                status=500
            )

        # Look for an existing order in the database
        order_exists = False
        attempt = 1
        while attempt <= 3:  # Reduced attempts
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details['name'],
                    email__iexact=billing_details['email'],
                    phone_number__iexact=shipping_details['phone'],
                    country__iexact=shipping_details['address']['country'],
                    postcode__iexact=shipping_details['address']['postal_code'],
                    town_or_city__iexact=shipping_details['address']['city'],
                    street_address1__iexact=shipping_details['address']['line1'],
                    street_address2__iexact=shipping_details['address']['line2'],
                    county__iexact=shipping_details['address']['state'],
                    grand_total_with_vat=grand_total_with_vat,
                    original_cart=cart,
                    stripe_pid=pid,
                    delivery_method=delivery_method,
                    delivery_cost=delivery_cost
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                logger.info(f'Order does not exist, retrying {attempt}/3')
                time.sleep(0.5)  # Reduced sleep time

        if order_exists:
            logger.info(f'Order already exists: {order}')
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200
            )

        # If no existing order, create a new one
        try:
            order = Order.objects.create(
                full_name=shipping_details['name'],
                email=billing_details['email'],
                phone_number=shipping_details['phone'],
                country=shipping_details['address']['country'],
                postcode=shipping_details['address']['postal_code'],
                town_or_city=shipping_details['address']['city'],
                street_address1=shipping_details['address']['line1'],
                street_address2=shipping_details['address']['line2'],
                county=shipping_details['address']['state'],
                original_cart=cart,
                stripe_pid=pid,
                vat_amount=Decimal(settings.VAT_RATE) * grand_total_with_vat,
                grand_total_with_vat=grand_total_with_vat,
                delivery_method=delivery_method,
                delivery_cost=delivery_cost,
            )

            # Process the items in the cart using bulk_create
            order_items = []
            for item_id, item_data in json.loads(cart).items():
                product = HennaProduct.objects.get(id=item_id)
                if isinstance(item_data, int):
                    order_items.append(OrderItem(
                        order=order,
                        product=product,
                        quantity=item_data,
                    ))
            OrderItem.objects.bulk_create(order_items)
            logger.info(f'Order created: {order}')
        except Exception as e:
            if order:
                order.delete()
            logger.error(f'Error creating order: {e}')
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: {e}',
                status=500
            )

        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200
        )

    def handle_payment_intent_payment_failed(self, event):
        """Handle the payment_intent.payment_failed webhook from Stripe"""
        logger.info(f'Payment failed: {event["type"]}')
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200
        )
