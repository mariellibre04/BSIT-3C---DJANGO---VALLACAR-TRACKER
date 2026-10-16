from django.contrib import admin

from .models import Bus


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('bus_number', 'plate_number', 'capacity', 'route', 'current_location', 'movement_status', 'status')
    search_fields = ('bus_number', 'plate_number', 'route', 'current_location')
    list_filter = ('status', 'movement_status')
