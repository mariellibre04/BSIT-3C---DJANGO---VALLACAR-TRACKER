from django.contrib import admin

from .models import Driver


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'license_number', 'contact', 'bus')
    search_fields = ('name', 'license_number', 'contact')
