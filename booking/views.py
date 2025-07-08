from django.http import JsonResponse
from datetime import datetime
from booking.utils import get_available_staff


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
