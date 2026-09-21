from django.db import models
from django.core.validators import RegexValidator
from datetime import date

class Room(models.Model):
    ROOM_TYPES = [
        ('SINGLE', 'Single'),
        ('DOUBLE', 'Double'),
        ('SUITE', 'Suite'),
        ('DELUXE', 'Deluxe'),
    ]
    
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.room_number} - {self.get_room_type_display()}"

class Guest(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    address = models.TextField()
    id_proof = models.CharField(max_length=50, help_text="ID type and number")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CHECKED_IN', 'Checked In'),
        ('CHECKED_OUT', 'Checked Out'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        old_room = None
        if self.pk:
            try:
                old_instance = Booking.objects.get(pk=self.pk)
                old_room = old_instance.room
            except Booking.DoesNotExist:
                pass

        if self.room and self.check_in_date and self.check_out_date:
            nights = (self.check_out_date - self.check_in_date).days
            if nights > 0:
                self.total_amount = self.room.price_per_night * nights
        super().save(*args, **kwargs)

        if old_room and old_room != self.room:
            has_active_old = Booking.objects.filter(
                room=old_room,
                status__in=['PENDING', 'CONFIRMED', 'CHECKED_IN']
            ).exists()
            if not has_active_old and not old_room.is_available:
                old_room.is_available = True
                old_room.save(update_fields=['is_available'])

        if self.room:
            if self.status in ['PENDING', 'CONFIRMED', 'CHECKED_IN']:
                if self.room.is_available:
                    self.room.is_available = False
                    self.room.save(update_fields=['is_available'])
            elif self.status in ['CHECKED_OUT', 'CANCELLED']:
                has_active = Booking.objects.filter(
                    room=self.room,
                    status__in=['PENDING', 'CONFIRMED', 'CHECKED_IN']
                ).exclude(pk=self.pk).exists()
                if not has_active and not self.room.is_available:
                    self.room.is_available = True
                    self.room.save(update_fields=['is_available'])

    def delete(self, *args, **kwargs):
        room = self.room
        super().delete(*args, **kwargs)
        if room:
            has_active = Booking.objects.filter(
                room=room,
                status__in=['PENDING', 'CONFIRMED', 'CHECKED_IN']
            ).exists()
            if not has_active and not room.is_available:
                room.is_available = True
                room.save(update_fields=['is_available'])

    def __str__(self):
        return f"Booking {self.id} - {self.guest} - Room {self.room.room_number}"
