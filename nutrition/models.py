from django.conf import settings
from django.db import models


class DietPlan(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="diet_plans",
        limit_choices_to={"role": "CLIENT"},
    )

    name = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    start_date = models.DateField()

    end_date = models.DateField(null=True, blank=True)

    calories_per_day = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.client.username}"


class Meal(models.Model):

    class MealType(models.TextChoices):
        BREAKFAST = "BREAKFAST", "Breakfast"
        MORNING_SNACK = "MORNING_SNACK", "Morning Snack"
        LUNCH = "LUNCH", "Lunch"
        EVENING_SNACK = "EVENING_SNACK", "Evening Snack"
        DINNER = "DINNER", "Dinner"

    diet_plan = models.ForeignKey(
        DietPlan,
        on_delete=models.CASCADE,
        related_name="meals",
    )

    meal_type = models.CharField(
        max_length=20,
        choices=MealType.choices,
    )

    name = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    calories = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    protein = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    carbohydrates = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    fats = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.diet_plan.name} - {self.get_meal_type_display()}"