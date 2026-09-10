from django.contrib import admin

from .models import ProgressRecord


@admin.register(ProgressRecord)
class ProgressRecordAdmin(admin.ModelAdmin):
    list_display = (
        "client",
        "date",
        "weight",
        "body_fat_percentage",
        "waist",
        "chest",
        "hips",
    )

    search_fields = (
        "client__user__username",
        "client__user__email",
    )

    list_filter = (
        "date",
    )

    ordering = (
        "-date",
    )