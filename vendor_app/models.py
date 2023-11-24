from django.db import models
from django.db.models import Avg, F, Sum
from django.utils import timezone
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


class Vendor(models.Model):
    name = models.CharField(max_length=255)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=50, unique=True)
    on_time_delivery_rate = models.FloatField(default=0.0)
    quality_rating_avg = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)
    fulfillment_rate = models.FloatField(default=0.0)
    token = models.OneToOneField(Token, on_delete=models.CASCADE, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.token:
            user = User.objects.create(username=f'vendor_{self.name}')
            self.token = Token.objects.create(user=user)
            self.save()
    
    def recalculate_metrics(self):
        completed_pos = PurchaseOrder.objects.filter(vendor=self, status='Completed')

        # Calculate on-time delivery rate
        total_completed_pos = completed_pos.count()
        self.on_time_delivery_rate = (
            completed_pos.filter(delivery_date__lte=F('acknowledgment_date')).count() / total_completed_pos
        ) * 100.0 if total_completed_pos > 0 else 0.0

        # Calculate quality rating average
        quality_rating_sum = completed_pos.exclude(quality_rating__isnull=True).aggregate(sum=Sum('quality_rating'))['sum']
        quality_rating_count = completed_pos.exclude(quality_rating__isnull=True).count()
        self.quality_rating_avg = quality_rating_sum / quality_rating_count if quality_rating_count > 0 else 0.0

        # Calculate average response time
        avg_response_time_seconds = completed_pos.exclude(acknowledgment_date__isnull=True).aggregate(
            average=Avg(F('acknowledgment_date') - F('issue_date'))
        )['average']
        self.average_response_time = avg_response_time_seconds.total_seconds() if avg_response_time_seconds else 0.0

        # Calculate fulfillment rate
        total_po_count = PurchaseOrder.objects.filter(vendor=self).count()
        self.fulfillment_rate = (
            completed_pos.filter(status='Completed').count() / total_po_count
        ) * 100.0 if total_po_count > 0 else 0.0

        self.save()

        # Update or create historical performance record
        HistoricalPerformance.objects.update_or_create(
            vendor=self,
            date=timezone.now(),
            defaults={
                'on_time_delivery_rate': self.on_time_delivery_rate,
                'quality_rating_avg': self.quality_rating_avg,
                'average_response_time': self.average_response_time,
                'fulfillment_rate': self.fulfillment_rate,
            }
        )
        
    def __str__(self):
        return self.name
    

class PurchaseOrder(models.Model):
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    SHIPMENT_SENT = 'Shipment Sent'
    DELIVERED = 'Completed'
    CANCELED = 'Canceled'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (SHIPMENT_SENT, 'Shipment Sent'),
        (DELIVERED, 'Completed'),
        (CANCELED, 'Canceled'),
    ]

    po_number = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='purchase_orders')
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=PENDING)
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField()
    acknowledgment_date = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Save the purchase order
        super().save(*args, **kwargs)

        # Update or create historical performance record after saving the purchase order
        if self.status == 'Completed' and self.vendor:
            self.vendor.recalculate_metrics()
         
    def acknowledge(self):
        """
        Method to handle acknowledgment of the purchase order.
        """
        if self.status == 'Accepted' and not self.acknowledgment_date:
            self.acknowledgment_date = timezone.now()
            self.save()


class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()
    
    def __str__(self):
        return f"{self.vendor.name} - {self.date}"