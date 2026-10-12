from django import forms
from django.utils import timezone
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
            "city",
            "health_goal",
            "height",
            "current_weight",
            "goal_weight",
            "dietary_preference",
            "medical_notes",
        ]
        widgets = {
            "phone": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "gender": forms.Select(
                attrs={"class": "form-select"}
            ),
            "country": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_country",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "id_city",
                }
            ),
            "health_goal": forms.Select(
                attrs={"class": "form-select"}
            ),
            "height": forms.NumberInput(attrs={"class": "form-control", "min": "1", "step": "0.01"}),
            "current_weight": forms.NumberInput(attrs={"class": "form-control", "min": "1", "step": "0.01"}),
            "goal_weight": forms.NumberInput(attrs={"class": "form-control", "min": "1", "step": "0.01"}),
            "dietary_preference": forms.Select(attrs={"class": "form-select"}),
            "medical_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Phone belongs to the registered account
        # and cannot be changed from the profile.
        self.fields["phone"].disabled = True
        self.fields["dietary_preference"].choices = [
            ("", "Select your usual diet type")
        ] + list(ClientProfile.DIETARY_PREFERENCE_CHOICES)
        self.fields["date_of_birth"].required = True
        self.fields["dietary_preference"].required = True

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get("date_of_birth")
        if dob and dob > timezone.localdate():
            raise forms.ValidationError("Date of birth cannot be in the future.")
        return dob

    def clean_dietary_preference(self):
        value = self.cleaned_data.get("dietary_preference")
        allowed = {choice[0] for choice in ClientProfile.DIETARY_PREFERENCE_CHOICES}
        if value not in allowed:
            raise forms.ValidationError("Select a valid dietary preference.")
        return value

    def clean(self):
        cleaned = super().clean()

        for field in ("height", "current_weight", "goal_weight"):
            value = cleaned.get(field)
            if value is not None and value <= 0:
                self.add_error(field, "Value must be greater than zero.")

        if not cleaned.get("city"):
            self.add_error(
                "city",
                "Please enter your city."
            )

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