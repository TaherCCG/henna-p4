from django.utils.html import format_html
from django.contrib import admin
from .models import HennaProduct, ProductsCategory, Discount

class DiscountInline(admin.TabularInline):
    model = HennaProduct.discounts.through
    extra = 1

@admin.register(HennaProduct)
class HennaProductAdmin(admin.ModelAdmin):
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
        'display_image',  # Custom method to display image thumbnail
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
        queryset.update(is_available=False)
    mark_as_unavailable.short_description = 'Mark selected products as unavailable'

    fieldsets = (
        (None, {
            'fields': ('sku', 'name', 'category')
        }),
        ('Pricing and Availability', {
            'fields': ('price', 'rating', 'stock_quantity', 'is_available'),
        }),
        ('Additional Information', {
            'fields': ('date_added', 'description', 'image', 'image_url'),
        }),
    )

    def get_discounted_price(self, obj):
        return obj.get_discounted_price()
    get_discounted_price.short_description = 'Discounted Price'

    def display_image(self, obj):
        """
        Display image thumbnail in the admin list view.
        """
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return 'No Image'
    display_image.short_description = 'Image'

@admin.register(ProductsCategory)
class ProductsCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )
    search_fields = (
        'name',
        'friendly_name',
    )
    prepopulated_fields = {'friendly_name': ('name',)}

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
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
        return obj.is_active()
    is_active_now.boolean = True
    is_active_now.short_description = 'Currently Active'
