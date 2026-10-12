from django.conf import settings
from django.db import models
from django.utils import timezone


class ClientProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"
        OTHER = "OTHER", "Other"
        PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY", "Prefer not to say"

    GOAL_CHOICES = [
        ("WEIGHT_LOSS", "Weight Loss"),
        ("FAT_LOSS", "Fat Loss"),
        ("WEIGHT_GAIN", "Weight Gain"),
        ("MUSCLE_GAIN", "Muscle Gain"),
        ("GENERAL_FITNESS", "General Fitness"),
        ("HEALTHY_LIFESTYLE", "Healthy Lifestyle"),
        ("OTHER", "Other"),
    ]

    DIETARY_PREFERENCE_CHOICES = [
        ("VEGETARIAN", "Vegetarian"),
        ("VEGETARIAN_EGGS", "Vegetarian + Eggs"),
        ("NON_VEGETARIAN", "Non-Vegetarian"),
        ("VEGAN", "Vegan"),
    ]

    COUNTRY_CHOICES = [
        ("IN", "India"),
        ("US", "United States"),
        ("GB", "United Kingdom"),
        ("AE", "United Arab Emirates"),
        ("CA", "Canada"),
        ("AU", "Australia"),
        ("OTHER", "Other"),
    ]

    INDIA_STATE_CHOICES = [
        ("Andhra Pradesh", "Andhra Pradesh"),
        ("Arunachal Pradesh", "Arunachal Pradesh"),
        ("Assam", "Assam"),
        ("Bihar", "Bihar"),
        ("Chhattisgarh", "Chhattisgarh"),
        ("Goa", "Goa"),
        ("Gujarat", "Gujarat"),
        ("Haryana", "Haryana"),
        ("Himachal Pradesh", "Himachal Pradesh"),
        ("Jharkhand", "Jharkhand"),
        ("Karnataka", "Karnataka"),
        ("Kerala", "Kerala"),
        ("Madhya Pradesh", "Madhya Pradesh"),
        ("Maharashtra", "Maharashtra"),
        ("Manipur", "Manipur"),
        ("Meghalaya", "Meghalaya"),
        ("Mizoram", "Mizoram"),
        ("Nagaland", "Nagaland"),
        ("Odisha", "Odisha"),
        ("Punjab", "Punjab"),
        ("Rajasthan", "Rajasthan"),
        ("Sikkim", "Sikkim"),
        ("Tamil Nadu", "Tamil Nadu"),
        ("Telangana", "Telangana"),
        ("Tripura", "Tripura"),
        ("Uttar Pradesh", "Uttar Pradesh"),
        ("Uttarakhand", "Uttarakhand"),
        ("West Bengal", "West Bengal"),
        ("Andaman and Nicobar Islands", "Andaman and Nicobar Islands"),
        ("Chandigarh", "Chandigarh"),
        ("Dadra and Nagar Haveli and Daman and Diu", "Dadra and Nagar Haveli and Daman and Diu"),
        ("Delhi", "Delhi"),
        ("Jammu and Kashmir", "Jammu and Kashmir"),
        ("Ladakh", "Ladakh"),
        ("Lakshadweep", "Lakshadweep"),
        ("Puducherry", "Puducherry"),
    ]

    assigned_dietitian = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_clients",
        limit_choices_to={"role": "DIETITIAN"},
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_profile",
    )
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=30, choices=Gender.choices, blank=True)
    country = models.CharField(max_length=10, choices=COUNTRY_CHOICES, default="IN")
    state = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    current_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    goal_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    health_goal = models.CharField(max_length=50, choices=GOAL_CHOICES, blank=True)
    dietary_preference = models.CharField(
        max_length=30,
        choices=DIETARY_PREFERENCE_CHOICES,
        blank=True,
    )
    medical_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def age(self):
        """Return the client's current age from DOB; age is never stored."""
        if not self.date_of_birth:
            return None

        today = timezone.localdate()
        years = today.year - self.date_of_birth.year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            years -= 1
        return years if years >= 0 else None

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Enrollment(models.Model):
    class Status(models.TextChoices):
        PROFILE_COMPLETE = "PROFILE_COMPLETE", "Profile Complete"
        PENDING_PAYMENT = "PENDING_PAYMENT", "Pending Payment"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    client = models.OneToOneField(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="enrollment",
    )
    membership_plan = models.ForeignKey(
        "payments.MembershipPlan",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="enrollments",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PROFILE_COMPLETE,
    )
    enrolled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client} - {self.get_status_display()}"
