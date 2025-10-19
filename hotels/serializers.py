from rest_framework import serializers
from django.utils import timezone
from .models import Hotel, Reservation, RoomType

class RoomTypeReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ['name', 'price_per_night', 'capacity']


class ReservationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    room_type = RoomTypeReservationSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id', 'user', 'room_type', 'check_in_date', 'check_out_date',
            'total_price', 'status', 'created_at'
        ]


class CreateReservationSerializer(serializers.Serializer):
    room_type_id = serializers.IntegerField()
    check_in_date = serializers.DateField()
    check_out_date = serializers.DateField()

    def validate_check_in_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("تاریخ ورود نمی‌تواند در گذشته باشد.")
        return value

    def validate(self, data):
        if data['check_in_date'] >= data['check_out_date']:
            raise serializers.ValidationError("تاریخ خروج باید بعد از تاریخ ورود باشد.")
        try:
            room_type = RoomType.objects.get(pk=data['room_type_id'])
        except RoomType.DoesNotExist:
            raise serializers.ValidationError("نوع اتاق مورد نظر یافت نشد.")

        overlapping_reservations = Reservation.objects.filter(
            room_type=room_type,
            status=Reservation.STATUS_CONFIRMED,
            check_in_date__lt=data['check_out_date'],
            check_out_date__gt=data['check_in_date']
        ).count()

        if overlapping_reservations >= room_type.inventory:
            raise serializers.ValidationError("متاسفانه در این بازه زمانی، اتاق خالی از این نوع وجود ندارد.")

        return data
    
class HotelPreViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['id', 'name', 'city', 'address']

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['id', 'name', 'city', 'address', 'description']


class RoomTypeSerializer(serializers.ModelSerializer):
    hotel = HotelSerializer(read_only=True)

    class Meta:
        model = RoomType
        fields = ['id', 'hotel', 'name', 'description', 'price_per_night', 'capacity', 'inventory']