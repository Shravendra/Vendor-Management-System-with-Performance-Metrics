from django.urls import path
from .views import (
    VendorListCreateView,
    VendorDetailsUpdateDeleteView,
    PurchaseOrderListCreateView,
    PurchaseOrderDetailsUpdateDeleteView,
    VendorPerformanceView,
    AcknowledgePurchaseOrderView
)

urlpatterns = [
    path('api/vendors/', VendorListCreateView.as_view(), name='vendor-list-create'),
    path('api/vendors/<int:pk>/', VendorDetailsUpdateDeleteView.as_view(), name='vendor-details-update-delete'),
    path('api/purchase_orders/', PurchaseOrderListCreateView.as_view(), name='purchase-order-list-create'),
    path('api/purchase_orders/<int:pk>/', PurchaseOrderDetailsUpdateDeleteView.as_view(), name='purchase-order-details-update-delete'),
    path('api/vendors/<int:pk>/performance/', VendorPerformanceView.as_view(), name='vendor-performance'),
    path('api/purchase_orders/<int:pk>/acknowledge/', AcknowledgePurchaseOrderView.as_view(), name='acknowledge-purchase-order'),
]