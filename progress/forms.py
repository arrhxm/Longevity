from django import forms

from .models import ProgressRecord, ProgressPhotoSet


MEASUREMENT_FIELDS = [
    "neck_circumference",
    "chest_circumference",
    "shoulder_circumference",
    "stomach_on_naval",
    "stomach_above_naval",
    "stomach_below_naval",
    "arms_flexed",
    "waist",
    "thighs_mid_section",
]


MEASUREMENT_LABELS = {
    "neck_circumference": "Neck circumference",
    "chest_circumference": "Chest circumference",
    "shoulder_circumference": "Shoulder circumference",
    "stomach_on_naval": "Stomach on the naval",
    "stomach_above_naval": "Stomach above the naval",
    "stomach_below_naval": "Stomach below the naval",
    "arms_flexed": "Arms Flexed",
    "waist": "Waist",
    "thighs_mid_section": "Thighs (Mid section above knee)",
}


def _measurement_widgets():
    return {
        field: forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "placeholder": "Inches",
            }
        )
        for field in MEASUREMENT_FIELDS
    }


class InitialMeasurementForm(forms.Form):
    height = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Height in cm"}),
    )
    weight = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Weight in kg"}),
    )
    neck_circumference = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Inches"}))
    chest_circumference = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Inches"}))
    shoulder_circumference = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Inches"}))
    stomach_on_naval = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Inches"}))
    stomach_above_naval = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Inches"}))
    stomach_below_naval = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Inches"}))
    arms_flexed = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Inches"}))
    waist = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Inches"}))
    thighs_mid_section = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Inches"}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Optional notes"}))


class WeeklyWeightForm(forms.Form):
    weight = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Weight in kg"}),
    )
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Optional notes"}))


class MonthlyMeasurementForm(forms.Form):
    weight = forms.DecimalField(max_digits=5, decimal_places=2, min_value=1, widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Weight in kg"}))
    neck_circumference = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, label=MEASUREMENT_LABELS["neck_circumference"], widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Inches"}))
    chest_circumference = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, label=MEASUREMENT_LABELS["chest_circumference"], widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Inches"}))
    shoulder_circumference = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, label=MEASUREMENT_LABELS["shoulder_circumference"], widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Inches"}))
    stomach_on_naval = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, label=MEASUREMENT_LABELS["stomach_on_naval"], widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Inches"}))
    stomach_above_naval = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, label=MEASUREMENT_LABELS["stomach_above_naval"], widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Inches"}))
    stomach_below_naval = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, label=MEASUREMENT_LABELS["stomach_below_naval"], widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Inches"}))
    arms_flexed = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, label=MEASUREMENT_LABELS["arms_flexed"], widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Inches"}))
    waist = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, label=MEASUREMENT_LABELS["waist"], widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Inches"}))
    thighs_mid_section = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, label=MEASUREMENT_LABELS["thighs_mid_section"], widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Inches"}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Optional notes"}))


class ProgressRecordForm(forms.ModelForm):
    class Meta:
        model = ProgressRecord
        fields = [
            "date",
            "record_type",
            "weight",
            *MEASUREMENT_FIELDS,
            "notes",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "record_type": forms.Select(attrs={"class": "form-select"}),
            "weight": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Weight in kg", "step": "0.01"}),
            **_measurement_widgets(),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Add notes about this progress record..."}),
        }


class ProgressPhotoForm(forms.Form):
    front_photo = forms.ImageField(required=False, label="Front (upper body)", widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}))
    side_photo = forms.ImageField(required=False, label="Side (upper body)", widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}))
    back_photo = forms.ImageField(required=False, label="Back (upper body)", widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}))


class ProgressPhotoSetForm(forms.ModelForm):
    class Meta:
        model = ProgressPhotoSet
        fields = ["front_photo", "side_photo", "back_photo"]
        labels = {
            "front_photo": "Front (upper body)",
            "side_photo": "Side (upper body)",
            "back_photo": "Back (upper body)",
        }
        widgets = {
            "front_photo": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "side_photo": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "back_photo": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }

    def clean(self):
        cleaned = super().clean()
        if not any(cleaned.get(name) for name in ("front_photo", "side_photo", "back_photo")):
            raise forms.ValidationError("Please upload at least one progress photo.")
        return cleaned
