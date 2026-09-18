from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from clients.models import ClientProfile
from notifications.models import Notification

from .forms import DietPlanForm, MealForm, OptionSectionForm, SectionForm
from .models import DietPlan, Meal, OptionSection, Section


def _require_dietitian(request):
    return request.user.role == "DIETITIAN"


@login_required
def create_diet_plan(request, client_id):
    if not _require_dietitian(request):
        return redirect("dashboard")

    client, _ = ClientProfile.objects.get_or_create(user_id=client_id)

    if request.method == "POST":
        form = DietPlanForm(request.POST)

        if form.is_valid():
            diet_plan = form.save(commit=False)
            diet_plan.client = client.user
            diet_plan.save()

            Notification.objects.create(
                user=client.user,
                notification_type=Notification.NotificationType.DIET_PLAN,
                title="New Diet Plan Assigned",
                message=(
                    f"Your dietitian has assigned you a new diet plan: "
                    f"{diet_plan.name}."
                ),
            )

            return redirect("diet_plan_detail", diet_plan_id=diet_plan.id)

    else:
        form = DietPlanForm()

    return render(
        request,
        "nutrition/create_diet_plan.html",
        {
            "form": form,
            "client": client,
        },
    )


@login_required
def edit_diet_plan(request, diet_plan_id):
    if not _require_dietitian(request):
        return redirect("dashboard")

    diet_plan = get_object_or_404(DietPlan, id=diet_plan_id)

    if request.method == "POST":
        form = DietPlanForm(request.POST, instance=diet_plan)

        if form.is_valid():
            form.save()
            return redirect("diet_plan_detail", diet_plan_id=diet_plan.id)

    else:
        form = DietPlanForm(instance=diet_plan)

    return render(
        request,
        "nutrition/create_diet_plan.html",
        {
            "form": form,
            "client": diet_plan.client.client_profile,
            "diet_plan": diet_plan,
            "editing": True,
        },
    )


@login_required
def diet_plan_detail(request, diet_plan_id):
    if not _require_dietitian(request):
        return redirect("dashboard")

    diet_plan = get_object_or_404(
        DietPlan.objects.select_related("client__client_profile"),
        id=diet_plan_id,
    )

    sections = (
        diet_plan.sections
        .prefetch_related("meals", "option_sections__meals")
        .all()
    )

    return render(
        request,
        "nutrition/diet_plan_detail.html",
        {
            "diet_plan": diet_plan,
            "sections": sections,
        },
    )


@login_required
def add_section(request, diet_plan_id):
    if not _require_dietitian(request):
        return redirect("dashboard")

    diet_plan = get_object_or_404(DietPlan, id=diet_plan_id)

    if request.method == "POST":
        form = SectionForm(request.POST)

        if form.is_valid():
            section = form.save(commit=False)
            section.diet_plan = diet_plan

            last_order = (
                diet_plan.sections.order_by("-order").values_list(
                    "order", flat=True
                ).first()
                or 0
            )
            section.order = last_order + 1
            section.save()

            return redirect("diet_plan_detail", diet_plan_id=diet_plan.id)

    else:
        form = SectionForm()

    return render(
        request,
        "nutrition/section_form.html",
        {
            "form": form,
            "diet_plan": diet_plan,
        },
    )


@login_required
def edit_section(request, section_id):
    if not _require_dietitian(request):
        return redirect("dashboard")

    section = get_object_or_404(Section, id=section_id)

    if request.method == "POST":
        form = SectionForm(request.POST, instance=section)

        if form.is_valid():
            form.save()
            return redirect("section_detail", section_id=section.id)

    else:
        form = SectionForm(instance=section)

    return render(
        request,
        "nutrition/section_form.html",
        {
            "form": form,
            "diet_plan": section.diet_plan,
            "section": section,
            "editing": True,
        },
    )


@login_required
def delete_section(request, section_id):
    if not _require_dietitian(request):
        return redirect("dashboard")

    section = get_object_or_404(Section, id=section_id)
    diet_plan_id = section.diet_plan_id

    if request.method == "POST":
        section.delete()

    return redirect("diet_plan_detail", diet_plan_id=diet_plan_id)


@login_required
def section_detail(request, section_id):
    if not _require_dietitian(request):
        return redirect("dashboard")

    section = get_object_or_404(
        Section.objects.select_related("diet_plan__client__client_profile"),
        id=section_id,
    )

    direct_meals = section.meals.filter(option_section__isnull=True)
    option_sections = section.option_sections.prefetch_related("meals")

    return render(
        request,
        "nutrition/section_detail.html",
        {
            "section": section,
            "diet_plan": section.diet_plan,
            "direct_meals": direct_meals,
            "option_sections": option_sections,
        },
    )


@login_required
def add_option_section(request, section_id):
    if not _require_dietitian(request):
        return redirect("dashboard")

    section = get_object_or_404(Section, id=section_id)

    if request.method == "POST":
        form = OptionSectionForm(request.POST)

        if form.is_valid():
            option_section = form.save(commit=False)
            option_section.section = section

            last_order = (
                section.option_sections.order_by("-order").values_list(
                    "order", flat=True
                ).first()
                or 0
            )
            option_section.order = last_order + 1
            option_section.save()

            return redirect("section_detail", section_id=section.id)

    else:
        form = OptionSectionForm()

    return render(
        request,
        "nutrition/option_section_form.html",
        {
            "form": form,
            "section": section,
        },
    )


@login_required
def edit_option_section(request, option_section_id):
    if not _require_dietitian(request):
        return redirect("dashboard")

    option_section = get_object_or_404(OptionSection, id=option_section_id)

    if request.method == "POST":
        form = OptionSectionForm(request.POST, instance=option_section)

        if form.is_valid():
            form.save()
            return redirect(
                "section_detail", section_id=option_section.section_id
            )

    else:
        form = OptionSectionForm(instance=option_section)

    return render(
        request,
        "nutrition/option_section_form.html",
        {
            "form": form,
            "section": option_section.section,
            "option_section": option_section,
            "editing": True,
        },
    )


@login_required
def delete_option_section(request, option_section_id):
    if not _require_dietitian(request):
        return redirect("dashboard")

    option_section = get_object_or_404(OptionSection, id=option_section_id)
    section_id = option_section.section_id

    if request.method == "POST":
        option_section.delete()

    return redirect("section_detail", section_id=section_id)


@login_required
def add_meal_to_section(request, section_id):
    if not _require_dietitian(request):
        return redirect("dashboard")

    section = get_object_or_404(Section, id=section_id)

    if request.method == "POST":
        form = MealForm(request.POST)

        if form.is_valid():
            meal = form.save(commit=False)
            meal.section = section

            last_order = (
                section.meals.order_by("-order").values_list(
                    "order", flat=True
                ).first()
                or 0
            )
            meal.order = last_order + 1
            meal.save()

            return redirect("section_detail", section_id=section.id)

    else:
        form = MealForm()

    return render(
        request,
        "nutrition/meal_form.html",
        {
            "form": form,
            "section": section,
        },
    )


@login_required
def add_meal_to_option_section(request, option_section_id):
    if not _require_dietitian(request):
        return redirect("dashboard")

    option_section = get_object_or_404(OptionSection, id=option_section_id)

    if request.method == "POST":
        form = MealForm(request.POST)

        if form.is_valid():
            meal = form.save(commit=False)
            meal.option_section = option_section

            last_order = (
                option_section.meals.order_by("-order").values_list(
                    "order", flat=True
                ).first()
                or 0
            )
            meal.order = last_order + 1
            meal.save()

            return redirect(
                "section_detail", section_id=option_section.section_id
            )

    else:
        form = MealForm()

    return render(
        request,
        "nutrition/meal_form.html",
        {
            "form": form,
            "option_section": option_section,
            "section": option_section.section,
        },
    )


@login_required
def edit_meal(request, meal_id):
    if not _require_dietitian(request):
        return redirect("dashboard")

    meal = get_object_or_404(Meal, id=meal_id)
    section = meal.parent_section

    if request.method == "POST":
        form = MealForm(request.POST, instance=meal)

        if form.is_valid():
            form.save()
            return redirect("section_detail", section_id=section.id)

    else:
        form = MealForm(instance=meal)

    return render(
        request,
        "nutrition/meal_form.html",
        {
            "form": form,
            "section": section,
            "option_section": meal.option_section,
            "meal": meal,
            "editing": True,
        },
    )


@login_required
def delete_meal(request, meal_id):
    if not _require_dietitian(request):
        return redirect("dashboard")

    meal = get_object_or_404(Meal, id=meal_id)
    section = meal.parent_section

    if request.method == "POST":
        meal.delete()

    return redirect("section_detail", section_id=section.id)
