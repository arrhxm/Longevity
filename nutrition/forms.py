from django import forms

from .models import DietPlan, Meal


class DietPlanForm(forms.ModelForm):

    class Meta:
        model = DietPlan

        fields = [
            "name",
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
                    "placeholder": "Example: Weight Loss Plan",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
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
class MealForm(forms.ModelForm):

    class Meta:
        model = Meal

        fields = [
            "meal_type",
            "name",
            "description",
            "calories",
            "protein",
            "carbohydrates",
            "fats",
        ]

        widgets = {
            "meal_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: Oatmeal with fruits",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Describe the meal...",
                }
            ),

            "calories": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Calories",
                }
            ),

            "protein": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Protein in grams",
                    "step": "0.01",
                }
            ),

            "carbohydrates": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Carbohydrates in grams",
                    "step": "0.01",
                }
            ),

            "fats": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Fats in grams",
                    "step": "0.01",
                }
            ),
        }