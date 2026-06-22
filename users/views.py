import secrets
import string

from rest_framework import generics, permissions, status
from rest_framework.views import APIView

from core.mixins import StandardResponseMixin
from core.utils.responses import StandardResponse
from users.models import User, VerificationCode
from users.serializers import (
    EmailVerificationSerializer,
    UserMeSerializer,
    UserRegistrationSerializer,
)
from .tasks import send_verification_code_email


class RequestVerificationCodeView(APIView):
    """Send a 6-digit verification code to the given email address."""

    serializer_class = EmailVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return StandardResponse.error(
                errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']

        user, created = User.objects.get_or_create(
            email=email,
            defaults={'is_active': False}
        )

        if not created and user.is_active:
            return StandardResponse.error(
                message='کاربری با این ایمیل قبلاً ثبت‌نام کرده و فعال است.',
                status=status.HTTP_409_CONFLICT
            )

        # Invalidate previous unused codes for this user before issuing a new one
        VerificationCode.objects.filter(user=user).delete()
        code = ''.join(secrets.choice(string.digits) for _ in range(6))
        VerificationCode.objects.create(user=user, code=code)
        send_verification_code_email.delay(email, code)

        return StandardResponse.success(
            message='کد تایید به ایمیل شما ارسال شد.',
            status=status.HTTP_200_OK
        )


class UserRegistrationView(StandardResponseMixin, generics.CreateAPIView):
    """Complete registration: validate the verification code and activate the user."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return StandardResponse.success(
            message='ثبت‌نام شما با موفقیت تکمیل شد.',
            status=status.HTTP_200_OK
        )


class UserMeView(StandardResponseMixin, generics.RetrieveUpdateAPIView):
    """Retrieve or update the profile of the currently authenticated user."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserMeSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user
