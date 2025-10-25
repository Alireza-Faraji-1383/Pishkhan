from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReservationViewSet , HotelViewSet , RoomTypeViewSet , HotelAdminViewSet , RoomTypeAdminViewSet

app_name = 'hotels'

router = DefaultRouter()
router.register(r'HotelAdmin', HotelAdminViewSet, basename='HotelAdmin')
router.register(r'RoomTypeAdmin', RoomTypeAdminViewSet, basename='RoomTypeAdmin')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'hotels', HotelViewSet, basename='hotel')
router.register(r'room-types', RoomTypeViewSet, basename='roomtype')

urlpatterns = [
    path('', include(router.urls)),
]