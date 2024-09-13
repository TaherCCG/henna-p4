from django.contrib import admin
from .models import HennaProduct, ProductsCategory, Discount

# Reference: https://docs.djangoproject.com/en/stable/ref/contrib/admin/#django.contrib.admin.TabularInline
class DiscountInline(admin.TabularInline):
    """
    Inline configuration for managing discounts associated with HennaProduct.
    """
    model = HennaProduct.discounts.through
    extra = 1


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
        'get_discounted_price',
        'rating',
        'stock_quantity',
        'is_available',
        'date_added',
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
    inlines = [DiscountInline]
    date_hierarchy = 'date_added'
    actions = ['mark_as_unavailable']

    def mark_as_unavailable(self, request, queryset):
        """
        Mark selected products as unavailable.
        """
        queryset.update(is_available=False)
    mark_as_unavailable.short_description = 'Mark selected products as unavailable'

    # Using `fieldsets` to organise fields on the edit form
    fieldsets = (
        (None, {
            'fields': ('sku', 'name', 'category')
        }),
        ('Pricing and Availability', {
            'fields': ('price', 'rating', 'stock_quantity', 'is_available'),
        }),
        ('Additional Information', {
            'fields': ('date_added', 'description'),
        }),
    )

    def get_discounted_price(self, obj):
        """
        Return the discounted price of the product.
        """
        return obj.get_discounted_price()
    get_discounted_price.short_description = 'Discounted Price'


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
    # Reference: https://docs.djangoproject.com/en/stable/ref/contrib/admin/#django.contrib.admin.ModelAdmin.prepopulated_fields
    prepopulated_fields = {'friendly_name': ('name',)}


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
        'is_active_now',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'discount_type',
        'active',
    )

    def is_active_now(self, obj):
        """
        Return whether the discount is currently active.
        """
        return obj.is_active()
    is_active_now.boolean = True
    is_active_now.short_description = 'Currently Active'
