from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from .views import RequestVerificationCodeView , UserRegistrationView , khApi

app_name = 'users'

urlpatterns = [
    path('register/send-code/', RequestVerificationCodeView.as_view(), name='register-send-code'),
    path('register/', UserRegistrationView.as_view(), name='register-complete'),

    path('kh/', khApi.as_view(), name='me'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]