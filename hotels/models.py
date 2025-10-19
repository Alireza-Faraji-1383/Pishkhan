from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Hotel(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hotels', verbose_name="صاحب هتل")
    name = models.CharField(max_length=200, verbose_name="نام هتل")
    city = models.CharField(max_length=100, verbose_name="شهر")
    address = models.TextField(verbose_name="آدرس")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "هتل"
        verbose_name_plural = "هتل‌ها"

    def __str__(self):
        return self.name


class RoomType(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='room_types', verbose_name="هتل")
    name = models.CharField(max_length=100, verbose_name="نوع اتاق")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت هر شب")
    capacity = models.PositiveSmallIntegerField(verbose_name="ظرفیت (نفر)")
    inventory = models.PositiveSmallIntegerField(verbose_name="تعداد موجود")

    class Meta:
        verbose_name = "نوع اتاق"
        verbose_name_plural = "انواع اتاق‌ها"

    def __str__(self):
        return f"{self.name} در هتل {self.hotel.name}"


class Reservation(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'در انتظار تایید'),
        (STATUS_CONFIRMED, 'تایید شده'),
        (STATUS_CANCELLED, 'کنسل شده'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations', verbose_name="کاربر")
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='reservations', verbose_name="نوع اتاق")
    check_in_date = models.DateField(verbose_name="تاریخ ورود")
    check_out_date = models.DateField(verbose_name="تاریخ خروج")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="قیمت کل")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name="وضعیت")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "رزرو"
        verbose_name_plural = "رزروها"
        ordering = ['-created_at']

    def __str__(self):
        return f"رزرو برای {self.user.username} در اتاق {self.room_type.name}"

# class Review(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name="کاربر")
#     hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews', verbose_name="هتل")
#     reservation = models.OneToOneField(Reservation, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="رزرو مرتبط")
#     rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="امتیاز")
#     comment = models.TextField(verbose_name="متن نظر")
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = "نظر"
#         verbose_name_plural = "نظرات"
#         constraints = [
#             models.UniqueConstraint(fields=['user', 'hotel'], name='unique_review_per_user_hotel')
#         ]
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"نظر از {self.user.username} برای هتل {self.hotel.name}"
