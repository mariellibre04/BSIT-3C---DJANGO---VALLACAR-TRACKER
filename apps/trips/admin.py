from django.contrib import admin

from .models import Trip


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('bus', 'origin', 'destination', 'scheduled_departure', 'status', 'delay_minutes')
    search_fields = ('origin', 'destination', 'route', 'bus__bus_number')
    list_filter = ('status',)
