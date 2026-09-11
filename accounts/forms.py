from django import forms

from clients.models import ClientProfile


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