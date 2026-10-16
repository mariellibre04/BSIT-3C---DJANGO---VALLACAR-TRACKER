"""Trips, delays, and analytics: completed trips, delays, utilization, routes."""

from django.conf import settings
from django.db import models


class Trip(models.Model):
    STATUS_SCHEDULED = 'scheduled'
    STATUS_EN_ROUTE = 'en_route'
    STATUS_ON_TIME = 'on_time'
    STATUS_DELAYED = 'delayed'
    STATUS_REROUTED = 'rerouted'
    STATUS_UNEXPECTED_STOP = 'unexpected_stop'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_EN_ROUTE, 'En Route'),
        (STATUS_ON_TIME, 'On Time'),
        (STATUS_DELAYED, 'Delayed'),
        (STATUS_REROUTED, 'Rerouted'),
        (STATUS_UNEXPECTED_STOP, 'Unexpected Stop'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    ALERT_STATUSES = {STATUS_DELAYED, STATUS_REROUTED, STATUS_UNEXPECTED_STOP}

    bus = models.ForeignKey(
        'bus.Bus',
        related_name='trips',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    route = models.CharField(max_length=255, blank=True, default='')
    scheduled_departure = models.DateTimeField()
    scheduled_arrival = models.DateTimeField()
    actual_departure = models.DateTimeField(null=True, blank=True)
    actual_arrival = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    delay_minutes = models.PositiveIntegerField(default=0)
    passenger_count = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, default='')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='trips',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tbltrip'
        ordering = ['-scheduled_departure']

    def __str__(self):
        bus_no = self.bus.bus_number if self.bus else 'Unassigned'
        return f'{bus_no}: {self.origin} -> {self.destination} ({self.get_status_display()})'

    @property
    def is_alert(self):
        return self.status in self.ALERT_STATUSES

    def compute_delay(self):
        """Recompute delay_minutes from scheduled vs actual arrival."""
        if self.actual_arrival and self.scheduled_arrival:
            delta = (self.actual_arrival - self.scheduled_arrival).total_seconds() / 60
            self.delay_minutes = max(0, int(delta))
        elif self.status == self.STATUS_DELAYED and not self.delay_minutes:
            pass
        return self.delay_minutes
