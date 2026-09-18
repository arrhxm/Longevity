from django import forms

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
            "health_goal",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "country": forms.Select(attrs={"class": "form-select", "id": "id_country"}),
            "state": forms.Select(attrs={"class": "form-select", "id": "id_state"}),
            "city": forms.TextInput(attrs={"class": "form-control", "id": "id_city", "placeholder": "Enter city"}),
            "health_goal": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date_of_birth"].required = True
        self.fields["gender"].required = True
        self.fields["country"].required = True
        self.fields["health_goal"].required = True
        self.fields["state"].required = False
        self.fields["city"].required = False
        self.fields["state"].choices = [("", "Select state")] + list(ClientProfile.INDIA_STATE_CHOICES)

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
