from django.contrib import admin
from .models import SuccessStory


@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "display_name",
        "starting_weight",
        "final_weight",
        "duration",
        "is_published",
        "display_order",
    )

    search_fields = (
        "title",
        "display_name",
        "description",
        "review",
    )

    list_filter = (
        "is_published",
    )

    ordering = (
        "display_order",
        "-created_at",
    )