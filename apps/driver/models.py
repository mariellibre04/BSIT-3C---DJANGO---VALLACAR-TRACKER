"""Driver records for Vallacar Tracker."""

from django.conf import settings
from django.db import models


class Driver(models.Model):
    name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=50, unique=True)
    contact = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255)
    bus = models.ForeignKey(
        'bus.Bus',
        related_name='drivers',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='drivers',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tbldriver'
        ordering = ['name']

    def __str__(self):
        return self.name
