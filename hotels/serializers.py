from rest_framework import serializers
from django.utils import timezone
from .models import Hotel, Reservation, RoomType, Review

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

        # overlapping_reservations = Reservation.objects.filter(
        #     room_type=room_type,
        #     status=Reservation.STATUS_CONFIRMED,
        #     check_in_date__lt=data['check_out_date'],
        #     check_out_date__gt=data['check_in_date']
        # ).count()

        # if overlapping_reservations >= room_type.inventory:
        #     raise serializers.ValidationError("متاسفانه در این بازه زمانی، اتاق خالی از این نوع وجود ندارد.")

        return data
    
class HotelPreViewSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = ['id', 'name', 'city', 'address', 'average_rating', 'total_reviews']

    def get_average_rating(self, obj):
        return obj.average_rating()

    def get_total_reviews(self, obj):
        return obj.total_reviews()

class HotelSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = ['id', 'name', 'city', 'address', 'description', 'average_rating', 'total_reviews']

    def get_average_rating(self, obj):
        return obj.average_rating()

    def get_total_reviews(self, obj):
        return obj.total_reviews()


class RoomTypeSerializer(serializers.ModelSerializer):
    hotel = HotelSerializer(read_only=True)

    class Meta:
        model = RoomType
        fields = ['id', 'hotel', 'name', 'description', 'price_per_night', 'capacity', 'inventory']


class RoomTypeCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = RoomType
        fields = ['id', 'hotel', 'name', 'description', 'price_per_night', 'capacity', 'inventory']


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    hotel = HotelSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'hotel', 'rating', 'comment', 'created_at', 'updated_at']


class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['hotel', 'rating', 'comment', 'reservation']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("امتیاز باید بین 1 تا 5 باشد.")
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        hotel = attrs.get('hotel')
        
        # Check if user has already reviewed this hotel
        if Review.objects.filter(user=user, hotel=hotel).exists():
            raise serializers.ValidationError("شما قبلاً برای این هتل نظر داده‌اید.")
        
        # Check if user has stayed at this hotel (has a confirmed reservation)
        reservation = attrs.get('reservation')
        if reservation:
            if reservation.user != user:
                raise serializers.ValidationError("رزرو مربوط به این کاربر نیست.")
            if reservation.room_type.hotel != hotel:
                raise serializers.ValidationError("رزرو مربوط به این هتل نیست.")
        else:
            # If no reservation provided, check if user has any confirmed reservation at this hotel
            user_has_reservation = Reservation.objects.filter(
                user=user,
                room_type__hotel=hotel,
                status=Reservation.STATUS_CONFIRMED
            ).exists()
            
            if not user_has_reservation:
                raise serializers.ValidationError("برای ثبت نظر باید حداقل یک بار در این هتل اقامت داشته باشید.")
        
        return attrs
