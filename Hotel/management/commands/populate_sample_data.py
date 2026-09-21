from django.core.management.base import BaseCommand
from hotel.models import Room, Guest, Booking
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Populate the database with sample data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating sample data...')
        
        # Create sample rooms
        rooms_data = [
            {'room_number': '101', 'room_type': 'SINGLE', 'price_per_night': 50.00, 'description': 'Cozy single room with city view'},
            {'room_number': '102', 'room_type': 'SINGLE', 'price_per_night': 55.00, 'description': 'Single room with garden view'},
            {'room_number': '201', 'room_type': 'DOUBLE', 'price_per_night': 80.00, 'description': 'Spacious double room with balcony'},
            {'room_number': '202', 'room_type': 'DOUBLE', 'price_per_night': 85.00, 'description': 'Double room with ocean view'},
            {'room_number': '301', 'room_type': 'SUITE', 'price_per_night': 150.00, 'description': 'Luxury suite with living area'},
            {'room_number': '302', 'room_type': 'SUITE', 'price_per_night': 175.00, 'description': 'Executive suite with jacuzzi'},
            {'room_number': '401', 'room_type': 'DELUXE', 'price_per_night': 200.00, 'description': 'Premium deluxe room with all amenities'},
            {'room_number': '402', 'room_type': 'DELUXE', 'price_per_night': 225.00, 'description': 'Ultra deluxe suite with private terrace'},
        ]
        
        for room_data in rooms_data:
            room, created = Room.objects.get_or_create(
                room_number=room_data['room_number'],
                defaults=room_data
            )
            if created:
                self.stdout.write(f'Created room: {room.room_number}')
        
        # Create sample guests
        guests_data = [
            {
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john.smith@email.com',
                'phone_number': '+1234567890',
                'address': '123 Main St, New York, NY 10001',
                'id_proof': 'Passport A12345678'
            },
            {
                'first_name': 'Jane',
                'last_name': 'Doe',
                'email': 'jane.doe@email.com',
                'phone_number': '+1987654321',
                'address': '456 Oak Ave, Los Angeles, CA 90001',
                'id_proof': 'Driver License DL9876543'
            },
            {
                'first_name': 'Michael',
                'last_name': 'Johnson',
                'email': 'michael.j@email.com',
                'phone_number': '+1555555555',
                'address': '789 Pine Rd, Chicago, IL 60601',
                'id_proof': 'National ID NI55555555'
            },
            {
                'first_name': 'Emily',
                'last_name': 'Williams',
                'email': 'emily.w@email.com',
                'phone_number': '+1444444444',
                'address': '321 Elm St, Houston, TX 77001',
                'id_proof': 'Passport B87654321'
            },
        ]
        
        for guest_data in guests_data:
            guest, created = Guest.objects.get_or_create(
                email=guest_data['email'],
                defaults=guest_data
            )
            if created:
                self.stdout.write(f'Created guest: {guest.first_name} {guest.last_name}')
        
        # Create sample bookings
        guests = Guest.objects.all()
        rooms = Room.objects.all()
        
        if guests.exists() and rooms.exists():
            # Create some confirmed bookings
            booking_data = [
                {
                    'guest': guests[0],
                    'room': rooms[0],
                    'check_in_date': date.today() + timedelta(days=1),
                    'check_out_date': date.today() + timedelta(days=4),
                    'status': 'CONFIRMED',
                    'special_requests': 'Late check-in requested'
                },
                {
                    'guest': guests[1],
                    'room': rooms[2],
                    'check_in_date': date.today() + timedelta(days=2),
                    'check_out_date': date.today() + timedelta(days=5),
                    'status': 'CONFIRMED',
                    'special_requests': 'Extra towels needed'
                },
                {
                    'guest': guests[2],
                    'room': rooms[4],
                    'check_in_date': date.today() - timedelta(days=2),
                    'check_out_date': date.today() + timedelta(days=3),
                    'status': 'CHECKED_IN',
                    'special_requests': 'Room service preferred'
                },
                {
                    'guest': guests[3],
                    'room': rooms[6],
                    'check_in_date': date.today() - timedelta(days=5),
                    'check_out_date': date.today() - timedelta(days=2),
                    'status': 'CHECKED_OUT',
                    'special_requests': 'Early check-out'
                },
            ]
            
            for data in booking_data:
                booking, created = Booking.objects.get_or_create(
                    guest=data['guest'],
                    room=data['room'],
                    check_in_date=data['check_in_date'],
                    defaults={
                        'check_out_date': data['check_out_date'],
                        'status': data['status'],
                        'special_requests': data['special_requests']
                    }
                )
                if created:
                    self.stdout.write(f'Created booking for {booking.guest}')
            
            # Mark some rooms as unavailable
            rooms[0].is_available = False
            rooms[0].save()
            rooms[2].is_available = False
            rooms[2].save()
            rooms[4].is_available = False
            rooms[4].save()
        
        self.stdout.write(self.style.SUCCESS('Sample data populated successfully!'))
