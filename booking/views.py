import json
from datetime import datetime

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render

from booking.utils import get_available_staff, get_available_slots, create_booking
from booking.models import Staff, Service


# apis
def available_staff_api(request):
    """
    API to return available staff for a given date.
    """
    date_str = request.GET.get("date")

    if not date_str:
        return JsonResponse({"error": "Missing date parameter"}, status=400)

    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse(
            {"error": "Invalid date format, use YYYY-MM-DD"}, status=400
        )

    staff_qs = get_available_staff(date_obj)
    data = list(staff_qs.values("id", "name"))

    return JsonResponse({"staff": data})


def available_slots_api(request):
    date_str = request.GET.get("date")
    service_id = request.GET.get("service_id")

    if not (date_str and service_id):
        return JsonResponse({"error": "Missing required parameters"}, status=400)

    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse(
            {"error": "Invalid date format, use YYYY-MM-DD"}, status=400
        )

    if date_obj < timezone.localdate():
        return JsonResponse({"slots": []})

    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        return JsonResponse({"error": "Invalid service ID"}, status=404)

    # Assign the first available staff
    available_staff = get_available_staff(date_obj).first()

    if not available_staff:
        return JsonResponse({"slots": [], "staff": None})

    slots = get_available_slots(date_obj, service.id, available_staff)
    return JsonResponse(
        {
            "slots": slots,
            "staff": {"id": available_staff.id, "name": available_staff.name},
        }
    )


@csrf_exempt
@require_POST
def book_appointment_api(request):
    """API to create bookings. Returns booking id and success message else responses with specific error message."""
    try:
        data = json.loads(request.body)
        service_id = data.get("service_id")
        staff_id = data.get("staff_id")
        customer_name = data.get("customer_name")
        customer_email = data.get("customer_email")
        date_str = data.get("date")
        start_time_str = data.get("start_time")
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not all(
        [service_id, staff_id, customer_name, customer_email, date_str, start_time_str]
    ):
        return JsonResponse({"error": "Missing required fields"}, status=400)

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
    except ValueError:
        return JsonResponse({"error": "Invalid date/time format"}, status=400)

    if date < timezone.localdate():
        return JsonResponse({"error": "Cannot book past date"}, status=400)

    try:
        service = Service.objects.get(id=service_id)
        staff = Staff.objects.get(id=staff_id)
    except (Service.DoesNotExist, Staff.DoesNotExist):
        return JsonResponse({"error": "Invalid staff or service"}, status=404)

    try:
        booking = create_booking(
            service=service,
            customer_name=customer_name,
            customer_email=customer_email,
            date=date,
            start_time=start_time,
            staff=staff,
        )
        return JsonResponse({"success": True, "booking_id": booking.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def services_api(request):
    """Returns all the services with name, duration, price and a specific id."""
    services = Service.objects.all().values("id", "name", "duration_minutes", "price")
    return JsonResponse({"services": list(services)})


# template views
def booking_page(request):
    return render(request, "booking/booking_form.html")
