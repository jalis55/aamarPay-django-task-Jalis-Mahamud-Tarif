import json
import requests
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import PaymentTransaction, FileUpload, ActivityLog
from .serializers import (
    FileUploadSerializer, 
    PaymentTransactionSerializer, 
    ActivityLogSerializer
)
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from .tasks import process_file  

from django.conf import settings
import time



class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user
        payment_data = {
            'store_id': settings.AAMARPAY_STORE_ID,
            'signature_key': settings.AAMARPAY_SIGNATURE_KEY,
            'amount': '100',
            'currency': 'BDT',
            'desc': 'File Upload Payment',
            'cus_name': user.username,
            'cus_email': user.email or f"{user.username}@example.com",
            'cus_phone': '01700000000',
            'success_url': request.build_absolute_uri('/api/payment/success/'),
            'fail_url': request.build_absolute_uri('/api/payment/fail/'),
            'cancel_url': request.build_absolute_uri('/api/payment/cancel/'),
            'tran_id': f"TXN{timezone.now().strftime('%Y%m%d%H%M%S')}",
            'type':'json'
        }

        # Send request to aamarPay
        try:
            response = requests.post(
                settings.AAMARPAY_ENDPOINT,
                data=json.dumps(payment_data)
            )
            response_data = response.json()

            if response_data.get('payment_url'):
                # Create payment transaction record
                PaymentTransaction.objects.create(
                    user=request.user,
                    transaction_id=payment_data['tran_id'],
                    amount=payment_data['amount'],
                    status='pending',
                    gateway_response=response_data
                )

                # Log activity
                ActivityLog.objects.create(
                    user=request.user,
                    action='payment_initiated',
                    metadata={
                        'transaction_id': payment_data['tran_id'],
                        'amount': payment_data['amount']
                    }
                )

                return Response({
                    'payment_url': response_data['payment_url'],
                    'transaction_id': payment_data['tran_id']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Payment initiation failed',
                    'details': response_data
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentSuccessView(APIView):
    def get(self, request):
        transaction_id = request.query_params.get('tran_id')
        payment_status = request.query_params.get('status')

        try:
            transaction = PaymentTransaction.objects.get(transaction_id=transaction_id)
            
            if payment_status == 'success':
                transaction.status = 'completed'
                transaction.save()
                
                # Log activity
                ActivityLog.objects.create(
                    user=transaction.user,
                    action='payment_success',
                    metadata={
                        'transaction_id': transaction_id,
                        'amount': str(transaction.amount)
                    }
                )
                
                return Response({
                    'status': 'Payment successful',
                    'file_upload_enabled': True
                }, status=status.HTTP_200_OK)
            else:
                transaction.status = 'failed'
                transaction.save()
                
                ActivityLog.objects.create(
                    user=transaction.user,
                    action='payment_failed',
                    metadata={
                        'transaction_id': transaction_id,
                        'amount': transaction.amount
                    }
                )
                
                return Response({
                    'status': 'Payment failed',
                    'file_upload_enabled': False
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except PaymentTransaction.DoesNotExist:
            return Response({
                'error': 'Transaction not found'
            }, status=status.HTTP_404_NOT_FOUND)

class PaymentHistoryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentTransactionSerializer
    
    def get_queryset(self):
        return PaymentTransaction.objects.filter(user=self.request.user).order_by('-timestamp')



class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if user has a successful payment
        has_paid = PaymentTransaction.objects.filter(
            user=request.user,
            status='completed'
        ).exists()
        
        if not has_paid:
            return Response({
                'error': 'Payment required before file upload'
            }, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        file_obj = request.FILES.get('file')
        
        if not file_obj:
            return Response({
                'error': 'No file provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file extension
        valid_extensions = ['.txt', '.docx']
        file_name = file_obj.name
        file_extension = os.path.splitext(file_name)[1].lower()
        
        if file_extension not in valid_extensions:
            return Response({
                'error': 'Invalid file type. Only .txt and .docx files are allowed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Save the file
        try:
            file_path = default_storage.save(f'uploads/{file_name}', ContentFile(file_obj.read()))
            
            # Create FileUpload record
            file_upload = FileUpload.objects.create(
                user=request.user,
                file=file_path,
                filename=file_name,
                status='processing'
            )
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='file_uploaded',
                metadata={
                    'filename': file_name,
                    'file_id': file_upload.id
                }
            )
            
            # Trigger Celery task
            process_file.delay(file_upload.id)

            
            return Response({
                'status': 'File uploaded successfully',
                'file_id': file_upload.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FileListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FileUploadSerializer
    
    def get_queryset(self):
        return FileUpload.objects.filter(user=self.request.user).order_by('-upload_time')

class ActivityLogListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ActivityLogSerializer
    
    def get_queryset(self):
        return ActivityLog.objects.filter(user=self.request.user).order_by('-timestamp')

  


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        has_paid = PaymentTransaction.objects.filter(user=user, status='completed').exists()
        
        files = FileUpload.objects.filter(user=user).order_by('-upload_time')
        activities = ActivityLog.objects.filter(user=user).order_by('-timestamp')
        transactions = PaymentTransaction.objects.filter(user=user).order_by('-timestamp')

        # Serialize the queryset data
        files_serializer = FileUploadSerializer(files, many=True)
        activities_serializer = ActivityLogSerializer(activities, many=True)
        transactions_serializer = PaymentTransactionSerializer(transactions, many=True)

        return Response({
            'has_paid': has_paid,
            'files': files_serializer.data,
            'activities': activities_serializer.data,
            'transactions': transactions_serializer.data,
        })