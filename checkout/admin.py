from django.contrib import admin
from .models import Order, OrderItem, Delivery


class OrderItemInline(admin.TabularInline):
    """
    Inline display for OrderItems in the OrderAdmin.
    Allows managing items directly from the order admin interface.
    """
    model = OrderItem
    extra = 0  # No extra empty forms displayed
    readonly_fields = ('product', 'quantity', 'price_at_order', 'get_total')

    def get_total(self, obj):
        """
        Calculate and display the total cost for the order item.
        """
        return obj.get_total()

    get_total.short_description = 'Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Orders.
    Displays the main fields for each order, along with calculated totals.
    """
    list_display = (
        'order_number', 'full_name', 'email', 'phone_number',
        'order_total', 'vat_amount','grand_total',
        'delivery_method', 'delivery_cost', 'grand_total_with_vat', 'date')
    
    readonly_fields = (
        'order_number', 'order_total', 'delivery_cost', 'vat_amount',
        'grand_total', 'grand_total_with_vat', 'date', 'original_cart',
        'stripe_pid')
    search_fields = ('order_number', 'full_name', 'email', 'phone_number')
    list_filter = ('delivery_method', 'date', 'grand_total_with_vat')
    inlines = [OrderItemInline]

    def save_model(self, request, obj, form, change):
        """
        Override save to update totals after saving the order.
        """
        super().save_model(request, obj, form, change)
        obj.update_total()


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Delivery methods.
    Displays the delivery method details and cost.
    """
    list_display = (
        'company_name', 'name', 'cost', 'estimated_delivery_time', 'active'
    )
    list_filter = ('active', 'company_name')
    search_fields = ('company_name', 'name')
    ordering = ('company_name', 'name')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Admin interface for managing individual OrderItems.
    Displays product, quantity, and price at order time.
    """
    list_display = ('order', 'product', 'quantity', 'price_at_order', 'get_total')
    readonly_fields = ('order', 'product', 'price_at_order', 'get_total')

    def get_total(self, obj):
        """
        Display the total price for the order item.
        """
        return obj.get_total()

    get_total.short_description = 'Total'
