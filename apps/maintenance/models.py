"""Bus maintenance monitoring: inspections, defects, and repair schedules."""

from django.conf import settings
from django.db import models


class MaintenanceRecord(models.Model):
    TYPE_INSPECTION = 'inspection'
    TYPE_PREVENTIVE = 'preventive'
    TYPE_REPAIR = 'repair'
    TYPE_DEFECT = 'defect'
    TYPE_CHOICES = [
        (TYPE_INSPECTION, 'Inspection'),
        (TYPE_PREVENTIVE, 'Preventive Maintenance'),
        (TYPE_REPAIR, 'Repair'),
        (TYPE_DEFECT, 'Reported Defect'),
    ]

    STATUS_SCHEDULED = 'scheduled'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_OVERDUE = 'overdue'
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_OVERDUE, 'Overdue'),
    ]

    bus = models.ForeignKey(
        'bus.Bus',
        related_name='maintenance_records',
        on_delete=models.CASCADE,
    )
    record_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_INSPECTION)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    inspection_date = models.DateField()
    next_due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='maintenance_records',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tblmaintenance'
        ordering = ['-inspection_date', '-created_at']

    def __str__(self):
        return f'{self.bus.bus_number} - {self.title} ({self.get_status_display()})'
