from django import forms

from .models import ProgressRecord


class ProgressRecordForm(forms.ModelForm):

    class Meta:
        model = ProgressRecord

        fields = [
            "date",
            "weight",
            "body_fat_percentage",
            "waist",
            "chest",
            "hips",
            "notes",
        ]

        widgets = {
            "date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "weight": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Weight in kg",
                    "step": "0.01",
                }
            ),

            "body_fat_percentage": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Body fat %",
                    "step": "0.01",
                }
            ),

            "waist": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Waist measurement",
                    "step": "0.01",
                }
            ),

            "chest": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Chest measurement",
                    "step": "0.01",
                }
            ),

            "hips": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Hip measurement",
                    "step": "0.01",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Add notes about this progress record...",
                }
            ),
        }