from django.contrib import admin
from .models import Delivery, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """
    Inline for managing order items directly within the order admin interface.
    """
    model = OrderItem
    fields = ('product', 'quantity', 'price_at_order', 'get_total')
    readonly_fields = ('price_at_order', 'get_total')
    extra = 1  # Can add one extra blank order item row


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    """
    Admin interface for managing delivery methods.
    Displays company details, cost, and estimated delivery time.
    """
    list_display = (
        'company_name', 'name', 'cost', 'estimated_delivery_time',
        'active', 'created_at', 'updated_at'
    )
    list_filter = ('active',)
    search_fields = ('company_name', 'name', 'details')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin interface for managing customer orders.
    Supports inline editing of order items and automatic total updates.
    """
    list_display = (
        'order_number', 'full_name', 'email', 'phone_number', 'country',
        'postcode', 'town_or_city', 'street_address1', 'street_address2',
        'county', 'date', 'order_total', 'delivery_cost', 'grand_total',
        'delivery_method'
    )
    list_filter = ('date', 'delivery_method', 'country', 'postcode')
    search_fields = (
        'order_number', 'full_name', 'email', 'phone_number', 'country',
        'postcode', 'town_or_city', 'street_address1', 'street_address2',
        'county'
    )
    readonly_fields = (
        'order_number', 'date', 'order_total', 'delivery_cost', 'grand_total'
    )
    inlines = [OrderItemInline]

    def save_model(self, request, obj, form, change):
        """
        Override save_model to ensure order totals are updated when the order is changed.
        """
        if change:  # Update totals only when editing an existing order
            obj.update_total()
        super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Admin interface for managing individual items in orders.
    Provides details about the product, quantity, and total price.
    """
    list_display = ('order', 'product', 'quantity', 'price_at_order', 'get_total')
    list_filter = ('order', 'product')
    search_fields = ('order__order_number', 'product__name')
    readonly_fields = ('price_at_order', 'get_total')

    def get_total(self, obj):
        """
        Calculate and display the total price for each order item.
        """
        return obj.get_total()

    get_total.short_description = 'Total Price'
