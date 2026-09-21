from rest_framework import serializers
from .models import Room, Guest, Booking

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class BookingSerializer(serializers.ModelSerializer):
    guest_name = serializers.CharField(source='guest', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    room_type = serializers.CharField(source='room.get_room_type_display', read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'total_amount']

    def validate(self, attrs):
        room = attrs.get('room')
        if not self.instance or (room and self.instance.room != room):
            if room and not room.is_available:
                raise serializers.ValidationError({"room": f"Room {room.room_number} is already booked and not available."})
        return attrs

class BookingDetailSerializer(serializers.ModelSerializer):
    guest = GuestSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'total_amount']

class RoomAvailabilitySerializer(serializers.Serializer):
    check_in_date = serializers.DateField()
    check_out_date = serializers.DateField()
    room_type = serializers.CharField(required=False)
