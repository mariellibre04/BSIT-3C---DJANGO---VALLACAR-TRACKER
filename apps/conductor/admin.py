from django.contrib import admin

from .models import Conductor


@admin.register(Conductor)
class ConductorAdmin(admin.ModelAdmin):
    list_display = ('name', 'employee_id', 'contact', 'bus')
    search_fields = ('name', 'employee_id', 'contact')
