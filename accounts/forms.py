from django import forms
from clients.models import ClientProfile
from django.contrib.auth import get_user_model


class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = [
            "phone",
            "date_of_birth",
            "gender",
            "country",
            "state",
            "city",
            "health_goal",
            "medical_notes",
        ]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "country": forms.Select(attrs={"class": "form-select", "id": "id_country"}),
            "state": forms.Select(attrs={"class": "form-select", "id": "id_state"}),
            "city": forms.TextInput(attrs={"class": "form-control", "id": "id_city"}),
            "health_goal": forms.Select(attrs={"class": "form-select"}),
            "medical_notes": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["state"].choices = [("", "Select state")] + list(ClientProfile.INDIA_STATE_CHOICES)
        # Phone belongs to the registered account and is not edited from the profile.
        self.fields["phone"].disabled = True

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("country") == "IN":
            if not cleaned.get("state"):
                self.add_error("state", "Please select your state.")
            if not cleaned.get("city"):
                self.add_error("city", "Please enter your city.")
        else:
            cleaned["state"] = ""
            cleaned["city"] = ""
        return cleaned

User = get_user_model()

class OTPRequestForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "First name",
            }
        ),
    )

    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Last name",
            }
        ),
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Email address",
            }
        ),
    )

    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Phone number",
            }
        ),
    )

    def clean_phone(self):
        phone = self.cleaned_data["phone"]

        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError(
                "This phone number is already registered."
            )

        return phone

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "This email is already registered."
            )

        return email
class CompleteRegistrationForm(forms.Form):
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Create password",
            }
        ),
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm password",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data