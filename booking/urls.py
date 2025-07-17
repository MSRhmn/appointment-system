from django.urls import path

from booking import views

urlpatterns = [
    # Template urls
    path("book/", views.booking_page, name="booking-page"),
    # My custom apis
    path("api/available-slots/", views.available_slots_api, name="available-slots-api"),
    path(
        "api/book-appointment/", views.book_appointment_api, name="book-appointment-api"
    ),
    path("api/services/", views.services_api, name="services-api"),
]
