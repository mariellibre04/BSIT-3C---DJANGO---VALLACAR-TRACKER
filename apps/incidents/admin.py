from django.contrib import admin

from .models import Incident


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('title', 'bus', 'incident_type', 'severity', 'status', 'created_at')
    search_fields = ('title', 'description', 'location')
    list_filter = ('incident_type', 'severity', 'status')
