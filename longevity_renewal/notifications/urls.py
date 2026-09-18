from django.urls import path

from .views import (
    notification_list,
    mark_notification_read,
    mark_all_notifications_read,
)

urlpatterns = [
    path(
        "",
        notification_list,
        name="notification_list",
    ),

    path(
        "<int:notification_id>/read/",
        mark_notification_read,
        name="mark_notification_read",
    ),

    path(
        "mark-all-read/",
        mark_all_notifications_read,
        name="mark_all_notifications_read",
    ),
]
