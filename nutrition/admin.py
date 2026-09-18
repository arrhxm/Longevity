from django.contrib import admin

from .models import DietPlan, Meal, OptionSection, Section


class MealInline(admin.TabularInline):
    model = Meal
    extra = 0


class OptionSectionInline(admin.TabularInline):
    model = OptionSection
    extra = 0


class SectionInline(admin.TabularInline):
    model = Section
    extra = 0


@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "client",
        "goal",
        "start_date",
        "end_date",
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

    inlines = [SectionInline]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = (
        "diet_plan",
        "name",
        "timing",
        "order",
    )

    list_filter = (
        "diet_plan",
    )

    search_fields = (
        "name",
        "diet_plan__name",
    )

    inlines = [OptionSectionInline, MealInline]


@admin.register(OptionSection)
class OptionSectionAdmin(admin.ModelAdmin):
    list_display = (
        "section",
        "name",
        "instruction",
        "order",
    )

    search_fields = (
        "name",
        "section__name",
    )

    inlines = [MealInline]


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "quantity",
        "unit",
        "section",
        "option_section",
    )

    search_fields = (
        "name",
        "section__name",
        "option_section__name",
    )
