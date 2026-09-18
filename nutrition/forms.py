from django import forms

from .models import DietPlan, Meal, OptionSection, Section, FoodLog



class DietPlanForm(forms.ModelForm):

    class Meta:
        model = DietPlan

        fields = [
            "name",
            "goal",
            "description",
            "start_date",
            "end_date",
            "calories_per_day",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: Atique Fat Loss Plan",
                }
            ),

            "goal": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: Fat Loss",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Describe the diet plan...",
                }
            ),

            "start_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "end_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "calories_per_day": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: 1800",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class SectionForm(forms.ModelForm):

    class Meta:
        model = Section

        fields = [
            "name",
            "timing",
            "description",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: Breakfast, Evening Snack",
                }
            ),

            "timing": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: 5:00 PM",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Example: Evening snack options",
                }
            ),
        }


class OptionSectionForm(forms.ModelForm):

    class Meta:
        model = OptionSection

        fields = [
            "name",
            "instruction",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: Option 1",
                }
            ),

            "instruction": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: Choose ONE",
                }
            ),
        }


class MealForm(forms.ModelForm):

    class Meta:
        model = Meal

        fields = [
            "name",
            "quantity",
            "unit",
            "notes",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: Roasted makhana",
                }
            ),

            "quantity": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: 25, 60-80",
                }
            ),

            "unit": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: g, ml, tablet",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Preparation / notes (optional)",
                }
            ),
        }


class FoodLogForm(forms.ModelForm):

    class Meta:
        model = FoodLog
        fields = ["option_section", "photo", "note"]
        widgets = {
            "option_section": forms.Select(attrs={"class": "form-select"}),
            "photo": forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "note": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Optional note about this meal...",
            }),
        }

    def __init__(self, *args, section=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["option_section"].queryset = (
            section.option_sections.all() if section is not None else OptionSection.objects.none()
        )
        self.fields["option_section"].required = False
        if section is not None and not section.option_sections.exists():
            self.fields.pop("option_section")

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and photo.size > 10 * 1024 * 1024:
            raise forms.ValidationError("Photo must be 10 MB or smaller.")
        if photo and getattr(photo, "content_type", "") and not photo.content_type.startswith("image/"):
            raise forms.ValidationError("Please upload an image file.")
        return photo


class FoodLogReviewForm(forms.ModelForm):

    class Meta:
        model = FoodLog
        fields = ["review_status", "dietitian_feedback"]
        widgets = {
            "review_status": forms.Select(attrs={"class": "form-select"}),
            "dietitian_feedback": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Write feedback for the client...",
            }),
        }
