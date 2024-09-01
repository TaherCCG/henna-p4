from django.db import models

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


class HennaProduct(models.Model):
    """
    Model representing a product in the Henna app.
    """
    category = models.ForeignKey('ProductsCategory', null=True, blank=True, on_delete=models.SET_NULL)
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name
