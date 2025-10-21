from django.contrib import admin
from .models import Hotel , RoomType ,Reservation

admin.site.register(Hotel)
admin.site.register(RoomType)
admin.site.register(Reservation)