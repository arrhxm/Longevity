from django.conf import settings
from django.db import models
from django.core.validators import FileExtensionValidator


class DietPlan(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="diet_plans",
        limit_choices_to={"role": "CLIENT"},
    )

    name = models.CharField(max_length=200)

    goal = models.CharField(
        max_length=200,
        blank=True,
        help_text="Example: Fat Loss, Toned Body & Fat Loss",
    )

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


class Section(models.Model):
    """
    A top-level block of a diet plan, e.g. "Breakfast", "Lunch",
    "Pre-Workout". A section can contain meals directly, option
    sections (alternatives to choose from), or both at once -- e.g. a
    Lunch section can list its main items directly *and* offer a
    "choose one" option section for the side dish.
    """

    diet_plan = models.ForeignKey(
        DietPlan,
        on_delete=models.CASCADE,
        related_name="sections",
    )

    name = models.CharField(
        max_length=200,
        help_text="Example: Breakfast, Lunch, Evening Snack",
    )

    timing = models.CharField(
        max_length=100,
        blank=True,
        help_text="Example: 8:00 AM, 15 minutes before breakfast",
    )

    description = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.diet_plan.name} - {self.name}"


class OptionSection(models.Model):
    """
    A set of alternatives nested inside a Section, e.g. "Option 1" /
    "Option 2" / "Option 3" for an evening snack, or the "Choose ONE"
    side-dish choice inside Lunch.
    """

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="option_sections",
    )

    name = models.CharField(
        max_length=200,
        help_text="Example: Option 1, Choose ONE",
    )

    instruction = models.CharField(
        max_length=200,
        blank=True,
        help_text="Example: Choose ONE",
    )

    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.section.name} - {self.name}"


class Meal(models.Model):
    """
    A single food item. Belongs to exactly one of Section (direct) or
    OptionSection (nested alternative) -- never both, never neither.
    """

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="meals",
        null=True,
        blank=True,
    )

    option_section = models.ForeignKey(
        OptionSection,
        on_delete=models.CASCADE,
        related_name="meals",
        null=True,
        blank=True,
    )

    name = models.CharField(
        max_length=200,
        help_text="Example: Roasted makhana, Chicken breast",
    )

    quantity = models.CharField(
        max_length=50,
        blank=True,
        help_text="Example: 25, 60-80, 2",
    )

    unit = models.CharField(
        max_length=50,
        blank=True,
        help_text="Example: g, ml, tablet, rotis",
    )

    notes = models.TextField(
        blank=True,
        help_text="Preparation notes, e.g. raw weight, air fried",
    )

    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(section__isnull=False, option_section__isnull=True)
                    | models.Q(section__isnull=True, option_section__isnull=False)
                ),
                name="meal_has_exactly_one_parent",
            )
        ]

    @property
    def parent_section(self):
        return self.section or (
            self.option_section.section if self.option_section else None
        )

    @property
    def diet_plan(self):
        parent = self.parent_section
        return parent.diet_plan if parent else None

    def __str__(self):
        quantity_display = f"{self.quantity} {self.unit}".strip()
        return f"{self.name} - {quantity_display}" if quantity_display else self.name


class FoodLog(models.Model):
    """A client's photo log for one diet-plan section/meal occasion."""

    class ReviewStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        FOLLOWED = "FOLLOWED", "Followed"
        PARTIALLY_FOLLOWED = "PARTIALLY_FOLLOWED", "Partially followed"
        NOT_FOLLOWED = "NOT_FOLLOWED", "Not followed"

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="food_logs",
        limit_choices_to={"role": "CLIENT"},
    )
    diet_plan = models.ForeignKey(
        DietPlan,
        on_delete=models.CASCADE,
        related_name="food_logs",
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="food_logs",
    )
    option_section = models.ForeignKey(
        OptionSection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="food_logs",
    )
    photo = models.FileField(
        upload_to="food_logs/%Y/%m/%d/",
        validators=[FileExtensionValidator(
            allowed_extensions=["jpg", "jpeg", "png", "webp"]
        )],
    )
    note = models.TextField(blank=True)
    # Snapshot of the meals and quantities assigned when this food log was submitted.
    # This keeps historical logs accurate even if the diet plan is edited later.
    prescribed_meals = models.JSONField(default=list, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    review_status = models.CharField(
        max_length=30,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )
    dietitian_feedback = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.client_id and self.diet_plan_id:
            if self.diet_plan.client_id != self.client_id:
                raise ValidationError("Food log client must match the diet plan client.")

        if self.section_id and self.diet_plan_id:
            if self.section.diet_plan_id != self.diet_plan_id:
                raise ValidationError("Section must belong to the selected diet plan.")

        if self.option_section_id and self.section_id:
            if self.option_section.section_id != self.section_id:
                raise ValidationError("Option section must belong to the selected section.")

    def __str__(self):
        return f"{self.client.username} - {self.section.name} - {self.uploaded_at:%Y-%m-%d %H:%M}"
