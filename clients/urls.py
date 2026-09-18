from django.urls import path

from .views import (
    enrollment_profile,
    enrollment_plan,
    enrollment_payment,
    renew_membership_plan,
    renewal_payment,
)

urlpatterns = [
    path("enrollment/", enrollment_profile, name="enrollment_profile"),
    path("enrollment/plan/", enrollment_plan, name="enrollment_plan"),
    path("enrollment/payment/", enrollment_payment, name="enrollment_payment"),
    path("renew/", renew_membership_plan, name="renew_membership_plan"),
    path("renew/payment/", renewal_payment, name="renewal_payment"),
]
