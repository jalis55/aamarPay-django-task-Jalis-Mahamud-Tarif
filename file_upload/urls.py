from django.urls import path
from .views import (
    InitiatePaymentView,
    PaymentSuccessView,
    FileUploadView,
    FileListView,
    ActivityLogListView,
    PaymentHistoryListView,
    DashboardView,
    # LoginView,
    # LogoutView,
    # user_dashboard,
)

urlpatterns = [
    path('api/initiate-payment/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('api/payment/success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('api/upload/', FileUploadView.as_view(), name='file-upload'),
    path('api/files/', FileListView.as_view(), name='file-list'),
    path('api/activity/', ActivityLogListView.as_view(), name='activity-list'),
    path('api/transactions/', PaymentHistoryListView.as_view(), name='transaction-list'),

    path('dashboard/', DashboardView.as_view(), name='dashboard-page'),
]