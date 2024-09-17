from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderItem

@receiver(post_save, sender=OrderItem)
def update_order_total_on_save(sender, instance, created, **kwargs):
    """
    Update order total on OrderItem creation or update.
    """
    instance.order.update_total()

@receiver(post_delete, sender=OrderItem)
def update_order_total_on_delete(sender, instance, **kwargs):
    """
    Update order total on OrderItem deletion.
    """
    instance.order.update_total()
