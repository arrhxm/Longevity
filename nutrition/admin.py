from django.contrib import admin

from .models import DietPlan, Meal


class MealInline(admin.TabularInline):
    model = Meal
    extra = 1


@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "client",
        "start_date",
        "end_date",
        "calories_per_day",
        "is_active",
    )

    search_fields = (
        "name",
        "client__username",
        "client__email",
    )

    list_filter = (
        "is_active",
        "start_date",
    )

    inlines = [MealInline]


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = (
        "diet_plan",
        "meal_type",
        "name",
        "calories",
        "protein",
        "carbohydrates",
        "fats",
    )

    list_filter = (
        "meal_type",
    )

    search_fields = (
        "name",
        "diet_plan__name",
        "diet_plan__client__username",
    )