from rest_framework import viewsets, mixins, status, permissions , filters
from rest_framework.decorators import action
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from core.utils.responses import StandardResponse
from core.mixins import StandardResponseMixin
from hotels.permissions import IsHotelAdmin
from core.permissions import IsOwner

from .models import Hotel, Reservation, RoomType
from .serializers import HotelPreViewSerializer, HotelSerializer, ReservationSerializer, CreateReservationSerializer, RoomTypeCreateSerializer, RoomTypeSerializer


class ReservationViewSet(StandardResponseMixin,mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user).select_related('room_type__hotel')

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateReservationSerializer
        return ReservationSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            with transaction.atomic():
                room_type = RoomType.objects.select_for_update().get(pk=data['room_type_id'])

                overlapping_reservations = Reservation.objects.filter(
                    room_type=room_type,
                    status=Reservation.STATUS_CONFIRMED,
                    check_in_date__lt=data['check_out_date'],
                    check_out_date__gt=data['check_in_date']
                ).count()

                if overlapping_reservations >= room_type.inventory:
                    return StandardResponse.error(errors="ظرفیت این اتاق در لحظه آخر تکمیل شد.", status=status.HTTP_409_CONFLICT)

                # محاسبه قیمت و ساخت رزرو
                duration = (data['check_out_date'] - data['check_in_date']).days
                total_price = duration * room_type.price_per_night

                reservation = Reservation.objects.create(
                    user=request.user,
                    room_type=room_type,
                    check_in_date=data['check_in_date'],
                    check_out_date=data['check_out_date'],
                    total_price=total_price,
                    status=Reservation.STATUS_CONFIRMED
                )
                
                read_serializer = ReservationSerializer(reservation)
                return StandardResponse.success(message='رزرو با موفقیت ایجاد شد.', data=read_serializer.data, status=status.HTTP_201_CREATED)

        except RoomType.DoesNotExist:
             return StandardResponse.error(message='نوع اتاق یافت نشد.', status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        
        if reservation.check_in_date <= timezone.now().date():
            return StandardResponse.error(errors="زمان مجاز برای کنسل کردن این رزرو گذشته است.", status=status.HTTP_400_BAD_REQUEST)
            
        reservation.status = Reservation.STATUS_CANCELLED
        reservation.save()
        
        read_serializer = ReservationSerializer(reservation)
        return StandardResponse.success(message='رزرو با موفقیت کنسل شد.', data=read_serializer.data, status=status.HTTP_200_OK)
    

class HotelViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Hotel.objects.all()
    def get_serializer_class(self):
        if self.action == 'list':
            return HotelPreViewSerializer
        return HotelSerializer
    filter_backends = [ filters.SearchFilter, filters.OrderingFilter ]
    search_fields = ['name', 'city', 'address']
    ordering_fields = ['created_at', 'name']


class RoomTypeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = RoomType.objects.select_related('hotel').all()
    serializer_class = RoomTypeSerializer
    filter_backends = [ filters.SearchFilter, filters.OrderingFilter ]
    search_fields = ['name', 'hotel__name', 'hotel__city']
    ordering_fields = ['price_per_night', 'capacity']



class HotelAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsHotelAdmin]
    serializer_class = HotelSerializer

    def get_queryset(self):
        return Hotel.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class RoomTypeAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsHotelAdmin]
    serializer_class = RoomTypeCreateSerializer

    def get_queryset(self):
        return RoomType.objects.filter(hotel__owner=self.request.user).select_related('hotel')
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)