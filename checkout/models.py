import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
from products.models import HennaProduct

class Delivery(models.Model):
    """
    Model representing delivery methods.
    Includes company name, cost, and estimated delivery time.
    """
    company_name = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    details = models.TextField()
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    estimated_delivery_time = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    """
    Model representing a customer's order, with support for free delivery above a threshold
    and discount handling.
    """
    order_number = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = models.CharField(max_length=40, null=False, blank=False)
    postcode = models.CharField(max_length=20, null=False, blank=False)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    delivery_method = models.ForeignKey(Delivery, on_delete=models.SET_NULL, null=True, blank=True)

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID.
        """
        return uuid.uuid4().hex.upper()

    def save(self, *args, **kwargs):
        """
        Override the save method to assign an order number if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def update_total(self):
        """
        Update the grand total for the order, considering discounts, free delivery threshold,
        and delivery costs.
        """
        # Calculate the total price of all items, considering discounts
        self.order_total = self.orderitems.aggregate(
            Sum('price_at_order'))['price_at_order__sum'] or 0

        # Check for free delivery threshold from settings
        if self.order_total >= settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = 0  # Apply free delivery
        else:
            self.delivery_cost = self.delivery_method.cost if self.delivery_method else 0

        # Calculate grand total (order total + delivery)
        self.grand_total = self.order_total + self.delivery_cost
        super().save()  # Ensure the updated totals are saved

    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(models.Model):
    """
    Model representing an individual item in an order.
    """
    order = models.ForeignKey(Order, related_name='orderitems', on_delete=models.CASCADE)
    product = models.ForeignKey(HennaProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=6, decimal_places=2)

    def save(self, *args, **kwargs):
        """
        Override save to set the price at order time, considering any active discounts.
        """
        if not self.price_at_order:
            self.price_at_order = self.product.get_discounted_price()
        super().save(*args, **kwargs)

    def get_total(self):
        """
        Calculate the total price for this item (quantity * price_at_order).
        """
        return self.price_at_order * self.quantity

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"
