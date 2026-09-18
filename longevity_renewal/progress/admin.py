from django.contrib import admin

from .models import ProgressRecord


@admin.register(ProgressRecord)
class ProgressRecordAdmin(admin.ModelAdmin):
    list_display = (
        "client",
        "date",
        "record_type",
        "weight",
        "neck_circumference",
        "chest_circumference",
        "shoulder_circumference",
        "stomach_on_naval",
        "stomach_above_naval",
        "stomach_below_naval",
        "arms_flexed",
        "waist",
        "thighs_mid_section",
    )
    search_fields = ("client__user__username", "client__user__email")
    list_filter = ("record_type", "date")
    ordering = ("-date",)
