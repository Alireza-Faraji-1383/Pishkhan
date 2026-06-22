from django.contrib import admin
from .models import Hotel, RoomType, Reservation, Review


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'owner')
    search_fields = ('name', 'city', 'address')
    list_filter = ('city',)


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'hotel', 'price_per_night', 'capacity', 'inventory')
    list_filter = ('hotel',)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'room_type', 'check_in_date', 'check_out_date', 'status')
    list_filter = ('status',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'hotel', 'rating', 'created_at')
    list_filter = ('rating', 'hotel')
    search_fields = ('comment',)
