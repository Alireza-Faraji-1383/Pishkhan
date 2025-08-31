from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import VerificationCode, User

@shared_task
def send_verification_code_email(email, code):
    subject = 'کد فعال‌سازی حساب کاربری'
    message = f'کد فعال‌سازی شما: {code}'
    email_from = "no-reply@example.com"
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

    return f"Verification email sent to {email}"