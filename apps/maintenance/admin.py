from django.contrib import admin

from .models import MaintenanceRecord


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ('bus', 'title', 'record_type', 'inspection_date', 'next_due_date', 'status')
    search_fields = ('title', 'description', 'bus__bus_number')
    list_filter = ('record_type', 'status')
