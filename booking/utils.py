from datetime import datetime, timedelta, time
from django.utils import timezone
from django.db import IntegrityError
from .models import AvailabilityRule, Booking, Service, Staff


def get_available_slots(date, service_id, staff):
    """
    Returns list of available start times for a given date, service, and staff.
    Only shows slots where no existing booking exists.
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

            # Only show slots if not already booked
            if not is_slot_conflicted(date, slot_start, service_duration, staff):
                slots.append(slot_start.strftime("%H:%M"))

            current_start += service_duration

    return slots


def is_slot_conflicted(date, slot_start_time, service_duration, staff):
    """
    Check if a given time range overlaps with existing bookings for a staff member.
    """
    slot_start_dt = datetime.combine(date, slot_start_time)
    slot_end_dt = slot_start_dt + service_duration

    # Fetch all bookings on that date and staff
    bookings = Booking.objects.filter(date=date, staff=staff)

    for booking in bookings:
        booking_start_dt = datetime.combine(date, booking.start_time)
        booking_end_dt = booking_start_dt + timedelta(
            minutes=booking.service.duration_minutes
        )

        if slot_start_dt < booking_end_dt and slot_end_dt > booking_start_dt:
            return True

    return False


def create_booking(service, customer_name, customer_email, date, start_time, staff):
    """
    Attempts to create a booking; relies on available slots and DB constraints to prevent conflicts.
    Raises IntegrityError if slot is already booked.
    """
    if date < timezone.localdate():
        raise Exception("Cannot book a past date.")

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
