from django.urls import path
from .views import login_view,user_dashboard
urlpatterns = [
    path('',login_view, name='login-page'),
    path('user-dashboard/', user_dashboard, name='user-dashboard'),
]