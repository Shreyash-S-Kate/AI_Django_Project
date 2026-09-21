from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import render
from .models import Room, Guest, Booking
from .serializers import RoomSerializer, GuestSerializer, BookingSerializer, BookingDetailSerializer

def index(request):
    return render(request, 'index.html')

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    @action(detail=False, methods=['get'])
    def available(self, request):
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        room_type = request.query_params.get('room_type')
        
        if not check_in or not check_out:
            return Response(
                {'error': 'check_in and check_out dates are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booked_rooms = Booking.objects.filter(
            Q(status='CONFIRMED') | Q(status='CHECKED_IN') | Q(status='PENDING'),
            check_in_date__lte=check_out,
            check_out_date__gte=check_in
        ).values_list('room_id', flat=True)
        
        available_rooms = Room.objects.filter(is_available=True).exclude(id__in=booked_rooms)
        
        if room_type:
            available_rooms = available_rooms.filter(room_type=room_type)
        
        serializer = self.get_serializer(available_rooms, many=True)
        return Response(serializer.data)

class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related('guest', 'room').all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        booking = serializer.save()
        if booking.status in ['PENDING', 'CONFIRMED', 'CHECKED_IN']:
            booking.room.is_available = False
            booking.room.save(update_fields=['is_available'])

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return BookingDetailSerializer
        return BookingSerializer

    @action(detail=False, methods=['get'])
    def by_guest(self, request):
        guest_id = request.query_params.get('guest_id')
        if not guest_id:
            return Response(
                {'error': 'guest_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bookings = self.queryset.filter(guest_id=guest_id)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_room(self, request):
        room_id = request.query_params.get('room_id')
        if not room_id:
            return Response(
                {'error': 'room_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bookings = self.queryset.filter(room_id=room_id)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        if booking.status != 'PENDING':
            return Response(
                {'error': 'Only pending bookings can be confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'CONFIRMED'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        booking = self.get_object()
        if booking.status != 'CONFIRMED':
            return Response(
                {'error': 'Only confirmed bookings can be checked in'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'CHECKED_IN'
        booking.room.is_available = False
        booking.room.save()
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def check_out(self, request, pk=None):
        booking = self.get_object()
        if booking.status != 'CHECKED_IN':
            return Response(
                {'error': 'Only checked-in bookings can be checked out'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'CHECKED_OUT'
        booking.room.is_available = True
        booking.room.save()
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status in ['CHECKED_IN', 'CHECKED_OUT']:
            return Response(
                {'error': 'Cannot cancel checked-in or checked-out bookings'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'CANCELLED'
        booking.room.is_available = True
        booking.room.save()
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)

