from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from .models import Vendor, PurchaseOrder, HistoricalPerformance, PurchaseOrder
from rest_framework.exceptions import ValidationError
from .serializers import VendorSerializer, PurchaseOrderSerializer, HistoricalPerformanceSerializer, AcknowledgePurchaseOrderSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


class VendorListCreateView(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def perform_create(self, serializer):
        try:
            serializer.save()
        except Exception as e:
            raise ValidationError(detail=str(e), code=status.HTTP_400_BAD_REQUEST)
    

class VendorDetailsUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def perform_update(self, serializer):
        try:
            serializer.save()
            # Recalculate metrics after updating
            serializer.instance.recalculate_metrics()
        except Exception as e:
            raise ValidationError(detail=str(e), code=status.HTTP_400_BAD_REQUEST)


class PurchaseOrderListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def perform_create(self, serializer):
        try:
            serializer.save()
        except Exception as e:
            raise ValidationError(detail=str(e), code=status.HTTP_400_BAD_REQUEST)


class PurchaseOrderDetailsUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def perform_update(self, serializer):
        try:
            serializer.save()
        except Exception as e:
            raise ValidationError(detail=str(e), code=status.HTTP_400_BAD_REQUEST)


class VendorPerformanceView(generics.RetrieveAPIView):
    serializer_class = HistoricalPerformanceSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        return HistoricalPerformance.objects.filter(vendor__id=vendor_id)
    
    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Calculate average values for each performance metric
        total_entries = queryset.count()
        if total_entries > 0:
            total_on_time_delivery_rate = sum(entry.on_time_delivery_rate for entry in queryset)
            total_quality_rating_avg = sum(entry.quality_rating_avg for entry in queryset)
            total_average_response_time = sum(entry.average_response_time for entry in queryset)
            total_fulfillment_rate = sum(entry.fulfillment_rate for entry in queryset)

            average_on_time_delivery_rate = total_on_time_delivery_rate / total_entries
            average_quality_rating_avg = total_quality_rating_avg / total_entries
            average_average_response_time = total_average_response_time / total_entries
            average_fulfillment_rate = total_fulfillment_rate / total_entries

            # Create a new instance with the calculated averages
            vendor_performance = HistoricalPerformance(
                vendor=queryset.first().vendor,
                date=queryset.first().date,
                on_time_delivery_rate=average_on_time_delivery_rate,
                quality_rating_avg=average_quality_rating_avg,
                average_response_time=average_average_response_time,
                fulfillment_rate=average_fulfillment_rate
            )

            serializer = self.get_serializer(vendor_performance)
            return Response(serializer.data)
        else:
            return Response({'detail': 'No historical performance data available.'}, status=status.HTTP_404_NOT_FOUND)


class AcknowledgePurchaseOrderView(generics.UpdateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = AcknowledgePurchaseOrderSerializer
    http_method_names = ['patch', 'post']

    def acknowledge(self, instance):
        if instance.status != 'Accepted':
            return Response({"detail": "Purchase order is not in 'Accepted' status."},
                            status=status.HTTP_400_BAD_REQUEST)

        instance.acknowledge()

        # Recalculate average_response_time
        instance.vendor.recalculate_metrics()

        return Response({"detail": "Purchase order acknowledged successfully."}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.acknowledge(instance)
    
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.acknowledge(instance)