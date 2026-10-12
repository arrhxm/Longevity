from django import forms
from django.utils import timezone

from .models import ClientProfile


class EnrollmentProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = [
            "date_of_birth",
            "gender",
            "country",
            "state",
            "city",
            "height",
            "current_weight",
            "health_goal",
            "dietary_preference",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "country": forms.Select(attrs={"class": "form-select", "id": "id_country"}),
            "state": forms.Select(attrs={"class": "form-select", "id": "id_state"}),
            "city": forms.TextInput(attrs={"class": "form-control", "id": "id_city", "placeholder": "Enter city"}),
            "height": forms.NumberInput(attrs={"class": "form-control", "min": "1", "step": "0.01", "placeholder": "Height in cm"}),
            "current_weight": forms.NumberInput(attrs={"class": "form-control", "min": "1", "step": "0.01", "placeholder": "Weight in kg"}),
            "health_goal": forms.Select(attrs={"class": "form-select"}),
            "dietary_preference": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "date_of_birth": "Date of Birth",
            "height": "Height (cm)",
            "current_weight": "Current Weight (kg)",
            "health_goal": "Goal",
            "dietary_preference": "Dietary Preference",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ("date_of_birth", "gender", "country", "health_goal", "dietary_preference", "height", "current_weight"):
            self.fields[field].required = True
        self.fields["state"].required = False
        self.fields["city"].required = False
        self.fields["state"].choices = [("", "Select state")] + list(ClientProfile.INDIA_STATE_CHOICES)
        self.fields["dietary_preference"].choices = [
            ("", "Select your usual diet type")
        ] + list(ClientProfile.DIETARY_PREFERENCE_CHOICES)

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get("date_of_birth")
        if dob and dob > timezone.localdate():
            raise forms.ValidationError("Date of birth cannot be in the future.")
        return dob

    def clean_height(self):
        value = self.cleaned_data.get("height")
        if value is not None and value <= 0:
            raise forms.ValidationError("Height must be greater than zero.")
        return value

    def clean_current_weight(self):
        value = self.cleaned_data.get("current_weight")
        if value is not None and value <= 0:
            raise forms.ValidationError("Weight must be greater than zero.")
        return value

    def clean(self):
        cleaned = super().clean()
        country = cleaned.get("country")
        if country == "IN":
            if not cleaned.get("state"):
                self.add_error("state", "Please select your state.")
            if not cleaned.get("city"):
                self.add_error("city", "Please enter your city.")
        else:
            cleaned["state"] = ""
            cleaned["city"] = ""
        return cleaned
