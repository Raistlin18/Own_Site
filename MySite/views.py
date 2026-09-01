from django.shortcuts import render

from .forms import ProductSearchForm
from .scraper import ScraperError, get_items


def index(request):
    return render(request, "MySite/index.html")


def projects(request):
    return render(request, "MySite/projects.html")


def scraper(request):
    form = ProductSearchForm(request.POST or None)
    context = {"form": form}

    if request.method == "POST" and form.is_valid():
        try:
            context["products"] = get_items(form.cleaned_data["product"])
        except ScraperError as exc:
            context["search_error"] = str(exc)

    return render(request, "MySite/scraper.html", context)
