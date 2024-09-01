from django.contrib import admin
from .models import HennaProduct, ProductsCategory

@admin.register(HennaProduct)
class HennaProductAdmin(admin.ModelAdmin):
    """
    Admin interface for managing HennaProduct instances.
    """
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'image',
    )
    ordering = ('sku',)
    search_fields = (
        'name',
        'sku',
        'description',
    )

@admin.register(ProductsCategory)
class ProductsCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for managing ProductsCategory instances.
    """
    list_display = (
        'friendly_name',
        'name',
    )
    search_fields = (
        'name',
        'friendly_name',
    )
