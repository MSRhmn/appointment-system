from django.urls import path

from booking import views

urlpatterns = [
    path("api/available-staff/", views.available_staff_api, name="available-staff-api"),
    path("api/available-slots/", views.available_slots_api, name="available-slots-api"),
    path(
        "api/book-appointment/", views.book_appointment_api, name="book-appointment-api"
    ),
    path("api/services/", views.services_api, name="services-api"),
]
