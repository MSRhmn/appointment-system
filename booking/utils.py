from datetime import datetime, timedelta, time
from django.utils import timezone
from django.db import IntegrityError
from .models import AvailabilityRule, Booking, Service, Staff


def get_available_slots(date, service_id, staff):
    """
    Returns list of available start times for given date, service, and staff.
    """
    slots = []

    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        return slots

    service_duration = timedelta(minutes=service.duration_minutes)

    # Filter availability for this staff on the given weekday
    availability_qs = AvailabilityRule.objects.filter(
        staff=staff,
        day_of_week=date.weekday(),
        is_active=True,
    )

    # Calculate current datetime
    now = timezone.localtime().time() if date == timezone.localdate() else None

    for rule in availability_qs:
        current_start = datetime.combine(date, rule.start_time)
        end_time = datetime.combine(date, rule.end_time)

        while current_start + service_duration <= end_time:
            slot_start = current_start.time()
            # Skip expired slots for today
            if now and slot_start <= now:
                current_start += service_duration
                continue

            # Only show if not already booked
            if not Booking.objects.filter(
                staff=staff, date=date, start_time=slot_start
            ).exists():
                slots.append(slot_start.strftime("%H:%M"))

            current_start += service_duration

    return slots


def create_booking(service, customer_name, customer_email, date, start_time, staff):
    """
    Safely create a booking only if within allowed available slots.
    """
    available_slots = get_available_slots(date, service.id, staff)

    if start_time.strftime("%H:%M") not in available_slots:
        raise Exception("This time slot is not available for booking.")

    try:
        return Booking.objects.create(
            service=service,
            staff=staff,
            customer_name=customer_name,
            customer_email=customer_email,
            date=date,
            start_time=start_time,
        )
    except IntegrityError:
        raise ("This time slot is already booked!")


def get_available_staff(date):
    """
    Returns all staff who have availability rules for given date.
    """
    return Staff.objects.filter(
        availabilityrule__day_of_week=date.weekday(), availabilityrule__is_active=True
    ).distinct()
