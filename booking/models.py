from django.db import models
from django.utils import timezone


# For services like haircut, massage, consultation etc.
class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField()  # How long it takes
    price = models.DecimalField(max_digits=8, decimal_places=2)
    buffer_minutes = models.PositiveIntegerField(default=0)  # Optional buffer time

    def __str__(self):
        return self.name


class Staff(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# Availability rules (working hours, days off)
class AvailabilityRule(models.Model):
    DAY_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        staff_name = self.staff.name
        return f"{staff_name} - {self.get_day_of_week_display()} {self.start_time} to {self.end_time}"


# Main booking model
class Booking(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Prevents duplicate data storing
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["staff", "date", "start_time"], name="unique_booking_per_slot"
            )
        ]

    def __str__(self):
        return f"{self.customer_name} - {self.service.name} on {self.date} at {self.start_time}"
