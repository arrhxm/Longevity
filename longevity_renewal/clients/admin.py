from django.contrib import admin

from .models import ClientProfile, Enrollment


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "gender", "country", "state", "city", "date_of_birth", "height", "current_weight", "goal_weight")
    search_fields = ("user__username", "user__email", "phone", "city")
    list_filter = ("country", "gender", "health_goal", "created_at")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("client", "membership_plan", "status", "enrolled_at", "created_at")
    list_filter = ("status", "membership_plan__country")
    search_fields = ("client__user__username", "client__user__email")
