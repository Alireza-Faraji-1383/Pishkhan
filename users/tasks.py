from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_verification_code_email(email, code):
    """Send the 6-digit verification code to the given email address."""
    subject = 'کد فعال‌سازی حساب کاربری'
    message = f'کد فعال‌سازی شما: {code}'
    email_from = 'no-reply@example.com'
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

    return f"Verification email sent to {email}"
