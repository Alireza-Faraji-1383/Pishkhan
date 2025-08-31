from django.db import models
from django.contrib.auth.models import AbstractUser

from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError

class User(AbstractUser):
    ROLE_CUSTOMER = 'customer'
    ROLE_HOTEL_OWNER = 'hotel_owner'
    
    ROLE_CHOICES = (
        (ROLE_CUSTOMER, 'مشتری'),
        (ROLE_HOTEL_OWNER, 'صاحب هتل'),
    )
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default=ROLE_CUSTOMER,
        verbose_name="نقش"
    )
    
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = ' کاربران'


    def __str__(self):
        return self.username
    
class VerificationCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)


    class Meta:
        verbose_name = 'کد تایید'
        verbose_name_plural = ' کد های تایید'

    def is_expired(self):
        return timezone.now() > (self.created_at + timedelta(minutes=10))

    def __str__(self):
        return f'{self.user.email} - {self.code}'