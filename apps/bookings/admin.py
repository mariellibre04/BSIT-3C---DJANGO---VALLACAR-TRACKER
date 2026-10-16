from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('reference', 'passenger_name', 'bus', 'pickup', 'seats', 'status', 'created_at')
    search_fields = ('reference', 'passenger_name', 'contact', 'pickup')
    list_filter = ('status',)
