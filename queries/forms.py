from django import forms
from .models import Query


class QueryForm(forms.ModelForm):
    class Meta:
        model = Query
        fields = ["subject"]
        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Diet Plan Question"}),
        }


class QueryMessageForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Write your message..."})
    )
