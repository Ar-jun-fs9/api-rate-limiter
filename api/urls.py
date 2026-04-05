# api/urls.py
from django.urls import path
from .views import  TestAPIView, HelloAPIView, LoginAPIView, PurchaseAPIView, ProfileAPIView
urlpatterns = [
    path('test/', TestAPIView.as_view(), name='test-api'),
    path('hello/', HelloAPIView.as_view(), name='hello-api'),
    path('login/', LoginAPIView.as_view(), name='login-api'),
    path('purchase/', PurchaseAPIView.as_view(), name='purchase-api'),
    path('profile/', ProfileAPIView.as_view(), name='profile-api'),
    
]