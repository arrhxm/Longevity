from django.urls import path

from .views import (
    initial_measurements,
    weekly_weight_update,
    monthly_measurement_update,
)

urlpatterns = [
    path("initial/", initial_measurements, name="initial_measurements"),
    path("weekly-weight/", weekly_weight_update, name="weekly_weight_update"),
    path("monthly-measurements/", monthly_measurement_update, name="monthly_measurement_update"),
]
