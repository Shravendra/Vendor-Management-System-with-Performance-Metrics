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
    queryset = HistoricalPerformance.objects.all()
    serializer_class = HistoricalPerformanceSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


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