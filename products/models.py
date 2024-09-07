from django.db import models
from django.utils import timezone

class ProductsCategory(models.Model):
    """
    Model representing a category for products.
    """
    name = models.CharField(max_length=254, unique=True)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Product Categories"

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name or self.name


class Discount(models.Model):
    """
    Model representing a discount that can be applied to products.
    Can be either percentage-based or a fixed amount.
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    name = models.CharField(max_length=100, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=6, decimal_places=2)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_discount_type_display()})"

    def is_active(self):
        """
        Check if the discount is currently active based on the active status and date range.
        """
        now = timezone.now()
        if self.active and (not self.start_date or self.start_date <= now) and (not self.end_date or self.end_date >= now):
            return True
        return False


class HennaProduct(models.Model):
    """
    Model representing a product in the Henna app.
    """
    category = models.ForeignKey('ProductsCategory', null=True, blank=True, on_delete=models.SET_NULL)
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)
    name = models.CharField(max_length=254, unique=True)
    description = models.TextField() 
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True) 
    stock_quantity = models.PositiveIntegerField(default=0) 
    is_available = models.BooleanField(default=True) 
    date_added = models.DateTimeField(default=timezone.now)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True) 

    discounts = models.ManyToManyField(Discount, blank=True) 

    def __str__(self):
        return self.name

    def get_current_discount(self):
        """
        Return the currently active discount applied to the product (if any).
        """
        active_discounts = self.discounts.filter(active=True)
        for discount in active_discounts:
            if discount.is_active():
                return discount
        return None

    def get_discounted_price(self):
        """
        Calculate the discounted price of the product, if any active discount applies.
        """
        discount = self.get_current_discount()
        if discount:
            if discount.discount_type == 'percentage':
                return self.price * (1 - (discount.value / 100))
            elif discount.discount_type == 'fixed':
                return max(self.price - discount.value, 0)
        return self.price
