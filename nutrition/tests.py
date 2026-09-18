from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from clients.models import ClientProfile

from .models import DietPlan, Meal, OptionSection, Section


class MealConstraintTests(TestCase):
    """
    A meal must belong to exactly one of Section or OptionSection.
    """

    def setUp(self):
        self.client_user = User.objects.create_user(
            username="nutrition_client", password="pass12345",
            role="CLIENT",
        )
        self.diet_plan = DietPlan.objects.create(
            client=self.client_user,
            name="Plan",
            start_date="2026-01-01",
        )
        self.section = Section.objects.create(
            diet_plan=self.diet_plan, name="Breakfast",
        )
        self.option_section = OptionSection.objects.create(
            section=self.section, name="Option 1",
        )

    def test_meal_with_only_section_is_valid(self):
        meal = Meal(section=self.section, name="Eggs")
        meal.full_clean()  # should not raise

    def test_meal_with_only_option_section_is_valid(self):
        meal = Meal(option_section=self.option_section, name="Dal")
        meal.full_clean()  # should not raise

    def test_meal_with_neither_parent_is_invalid(self):
        meal = Meal(name="Orphan Meal")
        with self.assertRaises(ValidationError):
            meal.full_clean()

    def test_meal_with_both_parents_is_invalid(self):
        meal = Meal(
            section=self.section,
            option_section=self.option_section,
            name="Confused Meal",
        )
        with self.assertRaises(ValidationError):
            meal.full_clean()


class HierarchicalDietPlanBuilderTests(TestCase):
    """
    Exercises the full dietitian workflow: create plan -> add section ->
    add meal directly -> add option section -> add meals to the option
    section. Mirrors the Enosha / Atique example plans.
    """

    def setUp(self):
        self.dietitian = User.objects.create_user(
            username="nutrition_dietitian", password="pass12345",
            role="DIETITIAN",
        )
        self.client_user = User.objects.create_user(
            username="nutrition_client2", password="pass12345",
            role="CLIENT",
        )
        ClientProfile.objects.create(user=self.client_user)
        self.client.login(
            username="nutrition_dietitian", password="pass12345"
        )

    def test_full_hierarchy_build(self):
        # 1. Create the plan
        response = self.client.post(
            reverse("create_diet_plan", args=[self.client_user.id]),
            {
                "name": "Atique Fat Loss Plan",
                "goal": "Fat Loss",
                "start_date": "2026-01-01",
                "is_active": "on",
            },
        )
        diet_plan = DietPlan.objects.get(name="Atique Fat Loss Plan")
        self.assertRedirects(
            response, reverse("diet_plan_detail", args=[diet_plan.id])
        )

        # 2. Add a Lunch section
        response = self.client.post(
            reverse("add_section", args=[diet_plan.id]),
            {"name": "Lunch", "timing": "1:00 PM"},
        )
        section = Section.objects.get(diet_plan=diet_plan, name="Lunch")
        self.assertRedirects(
            response, reverse("diet_plan_detail", args=[diet_plan.id])
        )

        # 3. Add meals directly to the section
        self.client.post(
            reverse("add_meal_to_section", args=[section.id]),
            {"name": "Chicken breast", "quantity": "100", "unit": "g"},
        )
        self.client.post(
            reverse("add_meal_to_section", args=[section.id]),
            {"name": "Cooked rice", "quantity": "150", "unit": "g"},
        )
        self.assertEqual(
            Meal.objects.filter(section=section).count(), 2
        )

        # 4. Add an option section ("Choose ONE") under Lunch
        response = self.client.post(
            reverse("add_option_section", args=[section.id]),
            {"name": "Choose ONE", "instruction": "Choose ONE"},
        )
        option_section = OptionSection.objects.get(
            section=section, name="Choose ONE"
        )
        self.assertRedirects(
            response, reverse("section_detail", args=[section.id])
        )

        # 5. Add meals inside the option section
        self.client.post(
            reverse(
                "add_meal_to_option_section", args=[option_section.id]
            ),
            {"name": "Cooked dal", "quantity": "60-80", "unit": "g"},
        )
        self.client.post(
            reverse(
                "add_meal_to_option_section", args=[option_section.id]
            ),
            {
                "name": "Homemade gravy",
                "quantity": "30-50",
                "unit": "g",
            },
        )
        self.assertEqual(
            Meal.objects.filter(option_section=option_section).count(),
            2,
        )

        # 6. Section detail page shows both direct meals and the
        # option section with its own meals.
        response = self.client.get(
            reverse("section_detail", args=[section.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chicken breast")
        self.assertContains(response, "Cooked rice")
        self.assertContains(response, "Choose ONE")
        self.assertContains(response, "Cooked dal")
        self.assertContains(response, "Homemade gravy")

    def test_multiple_option_sections_under_one_section(self):
        """
        Mirrors the Enosha evening-snack example: one section with
        three option sections, each offering its own alternative.
        """
        diet_plan = DietPlan.objects.create(
            client=self.client_user,
            name="Enosha Plan",
            start_date="2026-01-01",
        )
        section = Section.objects.create(
            diet_plan=diet_plan, name="Evening Snack",
        )

        for option_name, meal_name in [
            ("Option 1", "Roasted makhana"),
            ("Option 2", "Papaya"),
            ("Option 3", "Pineapple"),
        ]:
            option_section = OptionSection.objects.create(
                section=section, name=option_name,
            )
            Meal.objects.create(
                option_section=option_section,
                name=meal_name,
                quantity="25" if meal_name == "Roasted makhana" else "200",
                unit="g",
            )
            Meal.objects.create(
                option_section=option_section, name="Almonds", quantity="3",
            )

        self.assertEqual(section.option_sections.count(), 3)

        for option_section in section.option_sections.all():
            self.assertEqual(option_section.meals.count(), 2)

    def test_delete_meal_removes_only_that_meal(self):
        diet_plan = DietPlan.objects.create(
            client=self.client_user,
            name="Delete Test Plan",
            start_date="2026-01-01",
        )
        section = Section.objects.create(
            diet_plan=diet_plan, name="Breakfast",
        )
        meal_to_delete = Meal.objects.create(
            section=section, name="Toast",
        )
        meal_to_keep = Meal.objects.create(
            section=section, name="Eggs",
        )

        response = self.client.post(
            reverse("delete_meal", args=[meal_to_delete.id])
        )
        self.assertRedirects(
            response, reverse("section_detail", args=[section.id])
        )
        self.assertFalse(
            Meal.objects.filter(id=meal_to_delete.id).exists()
        )
        self.assertTrue(
            Meal.objects.filter(id=meal_to_keep.id).exists()
        )

    def test_delete_section_cascades_to_option_sections_and_meals(self):
        diet_plan = DietPlan.objects.create(
            client=self.client_user,
            name="Cascade Test Plan",
            start_date="2026-01-01",
        )
        section = Section.objects.create(
            diet_plan=diet_plan, name="Dinner",
        )
        option_section = OptionSection.objects.create(
            section=section, name="Option 1",
        )
        Meal.objects.create(option_section=option_section, name="Roti")

        self.client.post(reverse("delete_section", args=[section.id]))

        self.assertFalse(Section.objects.filter(id=section.id).exists())
        self.assertFalse(
            OptionSection.objects.filter(id=option_section.id).exists()
        )
        self.assertEqual(Meal.objects.count(), 0)
