from django.contrib import admin

from .models import Passenger


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'passenger_type', 'contact', 'bus')
    search_fields = ('name', 'contact', 'email')
    list_filter = ('passenger_type',)
