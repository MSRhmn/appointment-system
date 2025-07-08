from django.urls import path

from booking.views import available_staff_api

urlpatterns = [
    path("api/available-staff/", available_staff_api, name="available-staff-api")
]
