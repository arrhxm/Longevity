from django import forms
from clients.models import ClientProfile
from django.contrib.auth import get_user_model


class ClientProfileForm(forms.ModelForm):

    class Meta:
        model = ClientProfile

        fields = [
            "phone",
            "date_of_birth",
            "height",
            "current_weight",
            "goal_weight",
            "health_goal",
            "medical_notes",
        ]

        widgets = {
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter phone number",
                }
            ),

            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "height": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Height in cm",
                    "step": "0.01",
                }
            ),

            "current_weight": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Current weight",
                    "step": "0.01",
                }
            ),

            "goal_weight": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Goal weight",
                    "step": "0.01",
                }
            ),

            "health_goal": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Tell us about your health goals...",
                }
            ),

            "medical_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Add any relevant medical information...",
                }
            ),
        }

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