from django.contrib import admin
from .models import Service, AvailableSlot, ServiceCategory

# Register your models here.
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration', 'image')
    search_fields = ('name', 'description')


@admin.register(AvailableSlot)
class AvailableSlotAdmin(admin.ModelAdmin):
    list_display = ('service', 'date', 'time', 'is_booked')
    list_filter = ('service', 'date', 'is_booked')
    search_fields = ('service__name', 'date')


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for managing ServiceCategory.
    """
    list_display = (
        'friendly_name',
        'name',
    )
    search_fields = (
        'name',
        'friendly_name',
    )
