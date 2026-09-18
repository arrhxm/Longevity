from django.db import models
from clients.models import ClientProfile


class SuccessStory(models.Model):
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="success_stories",
    )

    display_name = models.CharField(
        max_length=100,
        help_text="Name shown publicly on the website.",
    )

    title = models.CharField(
        max_length=200,
        help_text="Example: 12 kg Weight Loss Journey",
    )

    description = models.TextField(
        blank=True,
        help_text="Short description of the client's journey.",
    )

    starting_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    final_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    duration = models.CharField(
        max_length=100,
        blank=True,
        help_text="Example: 4 months",
    )

    review = models.TextField(
        blank=True,
        help_text="Client testimonial.",
    )

    before_image = models.ImageField(
        upload_to="success_stories/before/",
        blank=True,
        null=True,
    )

    after_image = models.ImageField(
        upload_to="success_stories/after/",
        blank=True,
        null=True,
    )

    is_published = models.BooleanField(
        default=False,
        help_text="Show this success story on the public website.",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.title