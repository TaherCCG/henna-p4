from django.contrib import admin
from .models import HennaProduct, ProductsCategory, Discount

@admin.register(HennaProduct)
class HennaProductAdmin(admin.ModelAdmin):
    """
    Admin interface for managing HennaProduct.
    """
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'stock_quantity',
        'is_available',
        'date_added',
        'get_discounted_price',
    )
    ordering = ('sku',)
    search_fields = (
        'name',
        'sku',
        'description',
        'category__name', 
    )
    list_filter = (
        'category',
        'is_available',
        'date_added',
    )

@admin.register(ProductsCategory)
class ProductsCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for managing ProductsCategory.
    """
    list_display = (
        'friendly_name',
        'name',
    )
    search_fields = (
        'name',
        'friendly_name',
    )

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Discount.
    """
    list_display = (
        'name',
        'discount_type',
        'value',
        'start_date',
        'end_date',
        'active',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'discount_type',
        'active',
    )
