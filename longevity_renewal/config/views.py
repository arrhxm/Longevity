from django.shortcuts import render

from reviews.models import SuccessStory


def home(request):
    success_stories = SuccessStory.objects.filter(
        is_published=True
    ).order_by("display_order", "-created_at")[:6]

    return render(
        request,
        "home.html",
        {"success_stories": success_stories},
    )