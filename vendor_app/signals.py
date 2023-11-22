from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PurchaseOrder

@receiver(post_save, sender=PurchaseOrder)
@receiver(post_delete, sender=PurchaseOrder)
def update_metrics(sender, instance, **kwargs):
    # Update metrics for the associated vendor when a purchase order is saved or deleted
    if instance.vendor:
        instance.vendor.recalculate_metrics()