from django.contrib import admin
from .models import Service, Staff, AvailabilityRule, Booking


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_minutes", "price")
    search_fields = ("name",)
    list_editable = ("price",)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "email")


@admin.register(AvailabilityRule)
class AvailabilityRuleAdmin(admin.ModelAdmin):
    list_display = ("staff", "day_of_week", "start_time", "end_time", "is_active")
    list_filter = ("day_of_week", "is_active")
    search_fields = ("staff__name",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "service", "staff", "date", "start_time")
    list_filter = ("date", "staff", "service")
    search_fields = ("customer_name", "customer_email")
    readonly_fields = ("created_at",)
