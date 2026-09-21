from django.contrib import admin
from .models import Room, Guest, Booking

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'room_type', 'price_per_night', 'is_available', 'created_at']
    list_filter = ['room_type', 'is_available', 'created_at']
    search_fields = ['room_number', 'description']
    ordering = ['room_number']

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone_number', 'created_at']
    list_filter = ['created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    ordering = ['last_name', 'first_name']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'guest', 'room', 'check_in_date', 'check_out_date', 'status', 'total_amount']
    list_filter = ['status', 'check_in_date', 'check_out_date', 'room__room_type']
    search_fields = ['guest__first_name', 'guest__last_name', 'room__room_number']
    ordering = ['-created_at']
    date_hierarchy = 'check_in_date'
