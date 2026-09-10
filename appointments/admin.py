from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "client",
        "date",
        "time",
        "duration_minutes",
        "status",
        "reason",
    )

    search_fields = (
        "client__user__username",
        "client__user__email",
        "reason",
    )

    list_filter = (
        "status",
        "date",
    )

    ordering = (
        "-date",
        "-time",
    )