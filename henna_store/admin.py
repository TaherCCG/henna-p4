from django.contrib.admin import AdminSite, ModelAdmin, register
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# Importing models from other apps
from products.models import HennaProduct, ProductsCategory, Discount
from checkout.models import Delivery, Order, OrderItem
from profiles.models import UserProfile

class CustomAdminSite(AdminSite):
    site_header = "Henna Store Dashboard"
    site_title = "Henna Store Admin"
    index_title = "Welcome to the Henna Store Admin"

custom_admin_site = CustomAdminSite(name='custom_admin')

@register(HennaProduct)
class HennaProductAdmin(ModelAdmin):
    list_display = ('name', 'sku', 'category', 'price', 'is_available', 'date_added')
    search_fields = ('name', 'sku', 'category__name')
    list_filter = ('is_available', 'category')
    ordering = ('-date_added',)
    fieldsets = (
        (None, {
            'fields': ('name', 'sku', 'category', 'description', 'price', 
                       'stock_quantity', 'is_available', 'image_url', 'image')
        }),
        ('Additional Information', {
            'fields': ('rating', 'date_added'),
            'classes': ('collapse',),
        }),
    )

@register(ProductsCategory)
class ProductsCategoryAdmin(ModelAdmin):
    list_display = ('name', 'friendly_name')
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'friendly_name')
        }),
    )

@register(Discount)
class DiscountAdmin(ModelAdmin):
    list_display = ('name', 'discount_type', 'value', 'active', 'start_date', 'end_date')
    list_filter = ('discount_type', 'active')
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'discount_type', 'value', 'start_date', 'end_date', 'active')
        }),
    )

@register(Delivery)
class DeliveryAdmin(ModelAdmin):
    list_display = ('name', 'company_name', 'cost', 'active', 'estimated_delivery_time')
    search_fields = ('name', 'company_name')
    list_filter = ('active',)
    fieldsets = (
        (None, {
            'fields': ('name', 'company_name', 'details', 'cost', 
                       'estimated_delivery_time', 'active')
        }),
    )

@register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ('order_number', 'full_name', 'email', 'order_total', 'grand_total', 'date')
    search_fields = ('order_number', 'full_name', 'email')
    list_filter = ('date',)
    fieldsets = (
        (None, {
            'fields': ('order_number', 'user_profile', 'full_name', 'email', 
                       'phone_number', 'street_address1', 'street_address2', 
                       'town_or_city', 'postcode', 'county', 'country', 'date')
        }),
        ('Order Totals', {
            'fields': ('order_total', 'vat_amount', 'delivery_method', 
                       'delivery_cost', 'grand_total', 'stripe_pid', 'original_cart')
        }),
    )

@register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price_at_order')
    search_fields = ('order__order_number', 'product__name')
    list_filter = ('order',)
    fieldsets = (
        (None, {
            'fields': ('order', 'product', 'quantity', 'price_at_order')
        }),
    )

@register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ('user', 'default_phone_number', 'default_town_or_city', 'default_country')
    search_fields = ('user__username', 'default_phone_number', 'default_town_or_city')
    fieldsets = (
        (None, {
            'fields': ('user', 'default_phone_number', 'default_street_address1', 
                       'default_street_address2', 'default_town_or_city', 
                       'default_postcode', 'default_county', 'default_country')
        }),
    )

# Unregister existing models before registering them with custom admin site
admin.site.unregister(HennaProduct)
admin.site.unregister(ProductsCategory)
admin.site.unregister(Discount)
admin.site.unregister(Delivery)
admin.site.unregister(Order)
admin.site.unregister(OrderItem)
admin.site.unregister(UserProfile)

# Register models with custom admin site
custom_admin_site.register(HennaProduct, HennaProductAdmin)
custom_admin_site.register(ProductsCategory, ProductsCategoryAdmin)
custom_admin_site.register(Discount, DiscountAdmin)
custom_admin_site.register(Delivery, DeliveryAdmin)
custom_admin_site.register(Order, OrderAdmin)
custom_admin_site.register(OrderItem, OrderItemAdmin)
custom_admin_site.register(UserProfile, UserProfileAdmin)
