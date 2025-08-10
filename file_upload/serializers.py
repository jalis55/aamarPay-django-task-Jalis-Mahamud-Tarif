from rest_framework import serializers
from .models import FileUpload, PaymentTransaction, ActivityLog
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class FileUploadSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = FileUpload
        fields = ['id', 'user', 'file', 'filename', 'upload_time', 'status', 'word_count']
        read_only_fields = ['user', 'filename', 'upload_time', 'status', 'word_count']

class PaymentTransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = PaymentTransaction
        fields = ['id', 'user', 'transaction_id', 'amount', 'status', 'timestamp']
        read_only_fields = ['user', 'transaction_id', 'amount', 'status', 'timestamp']

class ActivityLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'action', 'metadata', 'timestamp']
        read_only_fields = ['user', 'action', 'metadata', 'timestamp']