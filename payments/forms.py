from django import forms

from .models import Membership, Payment


class MembershipForm(forms.ModelForm):

    class Meta:
        model = Membership

        fields = [
            "name",
            "start_date",
            "end_date",
            "amount",
            "status",
            "notes",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: 3 Month Weight Loss Plan",
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

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Membership amount",
                    "step": "0.01",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Add membership notes...",
                }
            ),
        }


class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment

        fields = [
            "amount",
            "payment_date",
            "payment_method",
            "status",
            "transaction_id",
            "notes",
        ]

        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Amount paid",
                    "step": "0.01",
                }
            ),

            "payment_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "payment_method": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "transaction_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Transaction ID (optional)",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Add payment notes...",
                }
            ),
        }