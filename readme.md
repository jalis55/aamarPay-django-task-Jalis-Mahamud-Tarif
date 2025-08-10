
# Payment Gateway with File Upload System

A Django application that integrates with aamarPay payment gateway and processes file uploads asynchronously using Celery.

## Features

- Payment processing via aamarPay sandbox
- File upload after successful payment
- Word count processing via Celery
- Activity logging
- REST API endpoints
- Bootstrap frontend
- Docker support

## Prerequisites

- Python 3.10+

- Django Rest Framework
- Redis
- Celery
- Docker (optional)

## Setup Instructions

### Local Development (Without Docker)
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/aamarPay-django-task-Jalis-Mahamud-Tarif.git

   cd aamarPay-django-task-Jalis-Mahamud-Tarif


2. **Set up virtual environment**
```bash
  python -m venv venv
 source venv/bin/activate  # On Windows:  venv\Scripts\activate
 ```
3. **Install dependencies**
  ```bash
   pip install -r requirements.txt
```
4. **Configure environment variables(.env file)**
```
AAMARPAY_STORE_ID=aamarpaytest
AAMARPAY_SIGNATURE_KEY=dbb74894e82415a2f7ff0ec3a97e4183
AAMARPAY_ENDPOINT=https://sandbox.aamarpay.com/jsonpost.php
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```
4. **Run redis**
```
redis-server
```
5. **Apply migrations**
```
python manage.py migrate
```
6. **python manage.py createsuperuser**
```
python manage.py createsuperuser
```
7. **Run the development server***
```
python manage.py runserver
```
8. **Run Celery worker**
new terminal
```
celery -A core worker --loglevel=info
```
### Docker Development
1. **Build and start containers**
```
Build and start containers
```
2. **Apply migrations**
```
docker-compose up --build
```
3. **Create Superuser**
```
docker-compose exec web python manage.py createsuperuser
```
4. **Access the application**
- Frontend: http://localhost:8000
- Admin: http://localhost:8000/admin

## Api Endpoints
| Endpoint | Method     | Description                |
| :-------- | :------- | :------------------------- |
| `/api/initiate-payment/` | `POST` | Initiate payment |
| `/api/payment/success` | `GET` | Payment success callback |
| `/api/upload/` | `POST` | File upload|
| `/api/files/` | `GET` | List user's files|
| `/api/activity/` | `GET` | List user's activities|
| `/api/transactions/` | `GET` | List payment history|





## project structure

```
.
├── core/               # Django project
├── file_upload/        # Main app
│   ├── models.py       # Database models
│   ├── tasks.py        # Celery tasks
│   ├── views.py        # API views
│   ├── urls.py         #urls 
|   └── ...
├── user_app            #frontend
│   ├── views.py        # API views
│   ├── urls.py         #urls 
│   ├── templates        #template directory 
|   └── ...
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker orchestration
├── requirements.txt    # Python dependencies
└── .env        # Environment variables template
```

## API Reference
### Authentication endpoints

1.**Obtain JWT Token** 
```http
POST /api/tokne/
```
### Request Body 
``` json
{
  "username":"your_user_name",
  "password":"your_password"
}

```
### Response (200 ok)
```json
{
  "refresh":"fjkdru84x...",
  "access":"iwoewpe3..."
}
```
2.**Refresh JWT Token
```http
POST /api/token/refresh/

```
### Request Body
```json
{
  "refresh":"your_refresh_token"
}
```
### Response (200 ok)
```json
{
  "access":"new_access_token"
}
```

All endpoints require JWT authentication:
```
Authorization: Bearer <your_token>
```
1. **Initiate Payment**
```http
POST /api/initiate-payment/
```
### Request Body
```bash
Headers:
  Authorization: Bearer <your_token>
  Content-Type: application/json
```
### Response (200 ok)
```json
{
  "payment_url": "https://sandbox.aamarpay.com/payment/...",
  "transaction_id": "TXN20230801123456"
}
```
2. **Payment Success Callback**
```bash
GET /api/payment/success?tran_id=TXN123&status=success
```
### Response
```
{
  "status": "Payment successful",
  "file_upload_enabled": true
}
```
3. **Upload File**
```bash
POST /api/upload/
```
### Request Body
```bash
Headers:
  Authorization: Bearer <your_token>
  Content-Type: multipart/form-data

Body:
  file: <file_binary_data>
```
### Response (201 created)
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "user@example.com"
  },
  "file": "/uploads/document.docx",
  "filename": "document.docx",
  "upload_time": "2023-08-01T12:34:56Z",
  "status": "processing",
  "word_count": null
}
```
4. **List user's file**
```bash
GET /api/files/
```
### Response (200 ok)
```json
[
  {
    "id": 1,
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "user@example.com"
    },
    "file": "/uploads/document.docx",
    "filename": "document.docx",
    "upload_time": "2023-08-01T12:34:56Z",
    "status": "completed",
    "word_count": 1500
  }
]
```
5. **List Payment History**
```bash
GET /api/transactions/
```
### Response (200 ok)
```json
[
  {
    "id": 1,
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "user@example.com"
    },
    "transaction_id": "TXN20230801123456",
    "amount": "100.00",
    "status": "completed",
    "timestamp": "2023-08-01T12:30:00Z"
  }
]
```
6. **List activity logs**
```bash
GET /api/activity/
```
### Response (200 ok)
```json
[
  {
    "id": 1,
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "user@example.com"
    },
    "action": "file_uploaded",
    "metadata": {
      "filename": "document.docx",
      "file_id": 1
    },
    "timestamp": "2023-08-01T12:35:00Z"
  }
]
```

## Example Usage

**New Token**
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'
```
**Initiate Payment**
```bash
curl -X POST http://localhost:8000/api/initiate-payment/ \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json"
```

**Get Payment History**
```bash
curl -X GET http://localhost:8000/api/transactions/ \
  -H "Authorization: Bearer your_jwt_token"
```

**Get activity Log**
```bash
curl -X GET http://localhost:8000/api/activity/ \
  -H "Authorization: Bearer your_jwt_token"
```

## Celery and Redis setup
``` bash
pip install celery Redis
```
## Configure Celery
celery.py
```
from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```
`__init__.py` should contain:

```python
from .celery import app as celery_app

__all__ = ["celery_app"]
```

settings.py
```
# Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
```
## Start service
local development (you can use docker)
```
# Terminal 1 - Redis
redis-server

# Terminal 2 - Celery Worker
celery -A core worker --loglevel=info

```
## Verify connection
```
# Check Redis
redis-cli ping  # Should return "PONG"

# Check Celery
celery -A core inspect ping
```



## aamarPay Sandbox Testing Guide

```bash
curl -X POST https://sandbox.aamarpay.com/jsonpost.php \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "aamarpaytest",
    "tran_id": "TEST12345",
    "success_url": "https://yourdomain.com/success",
    "fail_url": "https://yourdomain.com/fail",
    "cancel_url": "https://yourdomain.com/cancel",
    "amount": "10.00",
    "currency": "BDT",
    "signature_key": "dbb74894e82415a2f7ff0ec3a97e4183",
    "desc": "Test Payment via cURL",
    "cus_name": "Test User",
    "cus_email": "[email protected]",
    "cus_add1": "Dhaka",
    "cus_city": "Dhaka",
    "cus_country": "Bangladesh",
    "cus_phone": "+8801700000000",
    "type": "json"
  }'

```
- Endpoint (Sandbox): https://sandbox.aamarpay.com/jsonpost.php
- Required credentials:
  - store_id: aamarpaytest
  - signature_key: dbb74894e82415a2f7ff0ec3a97e4183
## Expected Response 
```json
{
    "result": "true",
    "payment_url": "https://sandbox.aamarpay.com/paynow.php?track=AAM1690275828103929"
}
```
- payment_url: Redirect your user to this URL to simulate the payment flow—in sandbox
- After completing or failing payment, aamarPay will redirect the user back to your specified success_url or fail_url, sending full transaction details via POST for your verification and handling. 
## Sample Response After Redirection
``` json
{
    "pg_service_charge_bdt": "2",
    "amount_original" : "100",
    "gateway_fee": "" ,
    "pg_service_charge_usd":"Not-Available" ,
    "pg_card_bank_name":"Not Available", 
    "pg_card_bank_country":"Not Available", 
    "card_number": "1234XXXXXXXXX123", 
    "card_holder": "" ,
    "status_code": "2" ,
    "pay_status": "Successful" ,
    "success_url": "http://localhost:3000/success.php", 
    "fail_url": "http://localhost:3000/fail.php", 
    "cus_name": "Customer Name", 
    "cus_email": "customer@test.com" ,
    "cus_phone": "0178273****", 
    "currency_merchant": "USD", 
    "convertion_rate": "109.57", 
    "ip_address": "XXX.XXX.XXX.XX" ,
    "other_currency": "40.00" ,
    "pg_txnid": "AAM1694948761103545" ,
    "epw_txnid": "AAM1694948761103545" ,
    "mer_txnid": "test1599957", 
    "store_id": "aamarpaytest" ,
    "merchant_id": "aamarpaytest" ,
    "currency": "BDT", 
    "store_amount": "4240.36" ,
    "pay_time": "2023-09-17 17:06:08", 
    "amount":  "4382.80" ,
    "bank_txn": "1094621001640" ,
    "card_type": "DBBL-VISA", 
    "reason": "Not Available", 
    "pg_card_risklevel": "0" ,
    "pg_error_code_details": "Not Available" ,
    "opt_a":"" ,
    "opt_b": "", 
    "opt_c": "" ,
    "opt_d": ""
}
```


[![GitHub License](https://img.shields.io/github/license/henriquesebastiao/badges?color=blue)](https://github.com/henriquesebastiao/badges/blob/main/LICENSE)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white) 
![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=flat&logo=bootstrap&logoColor=white)
![Javascript](https://img.shields.io/badge/JavaScript-323330?style=flat&logo=javascript&logoColor=F7DF1E)
