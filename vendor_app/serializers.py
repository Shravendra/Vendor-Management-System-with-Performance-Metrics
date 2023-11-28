from rest_framework import serializers
from .models import Vendor, PurchaseOrder, HistoricalPerformance
import re

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'

class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'

class HistoricalPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalPerformance
        fields = ['vendor', 'date', 'on_time_delivery_rate', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate']

class AcknowledgePurchaseOrderSerializer(serializers.Serializer):
    acknowledgment_date = serializers.DateTimeField()
