from datetime import datetime, timedelta, time
from django.utils import timezone
from .models import AvailabilityRule, Booking, Service, Staff


def get_available_slots(date, service_id, staff=None):
    """
    Returns list of available start times for given date, service, and staff (optional for solo providers).
    """
    slots = []

    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        return slots

    service_duration = timedelta(minutes=service.duration_minutes)

    # Filter rules for given staff or solo mode
    availability_qs = AvailabilityRule.objects.filter(
        day_of_week=date.weekday(),
        is_active=True,
    )

    if staff:
        availability_qs = availability_qs.filter(staff=staff)
    else:
        availability_qs = availability_qs.filter(staff__isnull=True)

    for rule in availability_qs:
        current_start = datetime.combine(date, rule.start_time)
        end_time = datetime.combine(date, rule.end_time)

        while current_start + service_duration <= end_time:
            slot_start = current_start.time()

            if not is_slot_conflicted(date, slot_start, staff):
                slots.append(slot_start.strftime("%H:%M"))

            current_start += service_duration

    return slots


def is_slot_conflicted(date, start_time, staff=None):
    """Check if a slot is already booked for given date and staff."""
    if staff is not None:
        conflict_exists = Booking.objects.filter(
            staff=staff, date=date, start_time=slot_start
        ).exists()
    else:
        conflict_exists = Booking.objects.filter(
            staff__isnull=True, date=date, start_time=slot_start
        ).exists()


def create_booking(
    service, customer_name, customer_email, date, start_time, staff=None
):
    """
    Safely create a booking with overlap prevention for both solo-provider and multi-staff.
    """
    if is_slot_conflicted(date, start_time, staff):
        raise Exception("This time slot is already booked!")

    return Booking.objects.create(
        service=service,
        staff=staff,
        customer_name=customer_name,
        customer_email=customer_email,
        date=date,
        start_time=start_time,
    )
