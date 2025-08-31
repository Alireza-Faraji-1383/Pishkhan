import secrets
import string

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status , generics , permissions

from core.mixins import StandardResponseMixin

from .tasks import send_verification_code_email
from core.utils.responses import StandardResponse

from users.models import User, VerificationCode
from users.serializers import EmailVerificationSerializer, UserRegistrationSerializer



class RequestVerificationCodeView(APIView):

    serializer_class = EmailVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return StandardResponse.error(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'is_active': False}
        )

        if not created and user.is_active:
            return StandardResponse.error('کاربری با این ایمیل قبلاً ثبت‌نام کرده و فعال است.', status=status.HTTP_409_CONFLICT)

        VerificationCode.objects.filter(user=user).delete()
        code = ''.join(secrets.choice(string.digits) for _ in range(6)) # generate random 6 digit code
        VerificationCode.objects.create(user=user, code=code)
        send_verification_code_email.delay(email, code)
        
        return StandardResponse.success('کد تایید به ایمیل شما ارسال شد.', status=status.HTTP_200_OK)
    

class UserRegistrationView(StandardResponseMixin, generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save() 
        
        
        return StandardResponse.success(message='ثبت‌ نام شما با موفقیت تکمیل شد.', status=status.HTTP_200_OK)
    

class khApi(APIView):
    def get(self, request):
        user = get_object_or_404(User, pk=request.user.pk)
        return StandardResponse.success(message=user.username, status=status.HTTP_200_OK)
