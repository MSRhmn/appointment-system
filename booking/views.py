from datetime import datetime
from django.http import JsonResponse
from django.utils import timezone

from booking.utils import get_available_staff, get_available_slots
from booking.models import Staff, Service


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
    staff_id = request.GET.get("staff_id")
    service_id = request.GET.get("service_id")

    if not (date_str and staff_id and service_id):
        return JsonResponse({"error": "Missing required parameters"}, status=400)

    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"error": "Invalid date format, use YYYY-MM-DD"}, status=400)

    if date_obj < timezone.localdate():
        return JsonResponse({"slots": []})

    try:
        staff = Staff.objects.get(id=staff_id)
        service = Service.objects.get(id=service_id)
    except (Staff.DoesNotExist, Service.DoesNotExist):
        return JsonResponse({"error": "Invalid staff or service ID"}, status=404)

    slots = get_available_slots(date_obj, service.id, staff)
    return JsonResponse({"slots": slots})
