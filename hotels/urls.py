from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReservationViewSet , HotelViewSet , RoomTypeViewSet

app_name = 'hotels'

router = DefaultRouter()
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'hotels', HotelViewSet, basename='hotel')
router.register(r'room-types', RoomTypeViewSet, basename='roomtype')

urlpatterns = [
    path('', include(router.urls)),
]