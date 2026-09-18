from django.urls import path

from .views import (
    add_meal_to_option_section,
    add_meal_to_section,
    add_option_section,
    add_section,
    create_diet_plan,
    delete_meal,
    upload_food_log, client_food_logs, dietitian_food_logs, review_food_log,
    delete_option_section,
    delete_section,
    diet_plan_detail,
    edit_diet_plan,
    edit_meal,
    edit_option_section,
    edit_section,
    section_detail,
)

urlpatterns = [
    path(
        "create/<int:client_id>/",
        create_diet_plan,
        name="create_diet_plan",
    ),
    path(
        "<int:diet_plan_id>/",
        diet_plan_detail,
        name="diet_plan_detail",
    ),
    path(
        "<int:diet_plan_id>/edit/",
        edit_diet_plan,
        name="edit_diet_plan",
    ),
    path(
        "<int:diet_plan_id>/section/add/",
        add_section,
        name="add_section",
    ),

    path(
        "section/<int:section_id>/",
        section_detail,
        name="section_detail",
    ),
    path(
        "section/<int:section_id>/edit/",
        edit_section,
        name="edit_section",
    ),
    path(
        "section/<int:section_id>/delete/",
        delete_section,
        name="delete_section",
    ),
    path(
        "section/<int:section_id>/meal/add/",
        add_meal_to_section,
        name="add_meal_to_section",
    ),
    path(
        "section/<int:section_id>/option-section/add/",
        add_option_section,
        name="add_option_section",
    ),

    path(
        "option-section/<int:option_section_id>/edit/",
        edit_option_section,
        name="edit_option_section",
    ),
    path(
        "option-section/<int:option_section_id>/delete/",
        delete_option_section,
        name="delete_option_section",
    ),
    path(
        "option-section/<int:option_section_id>/meal/add/",
        add_meal_to_option_section,
        name="add_meal_to_option_section",
    ),

    path(
        "meal/<int:meal_id>/edit/",
        edit_meal,
        name="edit_meal",
    ),
    path(
        "meal/<int:meal_id>/delete/",
        delete_meal,
        name="delete_meal",
    ),

    path("food-log/upload/<int:section_id>/", upload_food_log, name="upload_food_log"),
    path("my-food-logs/", client_food_logs, name="client_food_logs"),
    path("food-logs/", dietitian_food_logs, name="dietitian_food_logs"),
    path("food-log/<int:food_log_id>/review/", review_food_log, name="review_food_log"),
]
