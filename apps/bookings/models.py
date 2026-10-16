"""Passenger seat bookings: riders reserve seats, drivers/conductors get notified."""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum


class Booking(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_DECLINED = 'declined'
    STATUS_CANCELLED = 'cancelled'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_DECLINED, 'Declined'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_COMPLETED, 'Completed'),
    ]
    ACTIVE_STATUSES = {STATUS_PENDING, STATUS_CONFIRMED}

    bus = models.ForeignKey(
        'bus.Bus',
        related_name='bookings',
        on_delete=models.CASCADE,
    )
    passenger_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=50)
    pickup = models.CharField(
        max_length=255,
        help_text='Terminal / waiting place where the rider will board.',
    )
    seats = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reference = models.CharField(max_length=20, unique=True, blank=True, default='')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='bookings',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tblbooking'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reference or "BK-?"}: {self.passenger_name} x{self.seats} ({self.get_status_display()})'

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)
        if creating and not self.reference:
            self.reference = f'BK-{self.id:06d}'
            super().save(update_fields=['reference'])

    @property
    def is_active(self):
        return self.status in self.ACTIVE_STATUSES


def active_holds(bus_id):
    """Seats currently held by pending + confirmed bookings for a bus."""
    total = Booking.objects.filter(
        bus_id=bus_id, status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED]
    ).aggregate(v=Sum('seats'))['v']
    return total or 0
