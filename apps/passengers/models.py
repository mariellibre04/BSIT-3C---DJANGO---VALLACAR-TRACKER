"""Passenger records for Vallacar Tracker."""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Passenger(models.Model):
    TYPE_STUDENT = 'student'
    TYPE_SENIOR = 'senior'
    TYPE_REGULAR = 'regular'
    TYPE_PWD = 'pwd'
    TYPE_CHOICES = [
        (TYPE_STUDENT, 'Student'),
        (TYPE_SENIOR, 'Senior Citizen'),
        (TYPE_REGULAR, 'Regular'),
        (TYPE_PWD, 'PWD'),
    ]

    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(150)]
    )
    passenger_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default=TYPE_REGULAR
    )
    contact = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True)
    bus = models.ForeignKey(
        'bus.Bus',
        related_name='passengers',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='passengers',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tblpassenger'
        ordering = ['name']

    def __str__(self):
        return self.name
