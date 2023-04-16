from django.shortcuts import render
from django.http import HttpResponseRedirect
from .scraper import get_items as gi
from tqdm.auto import tqdm


# Create your views here.
def index(response):
    return render(response, 'MySite/index.html')

def projects(response):
    return render(response, 'MySite/projects.html')

def scraper(response):
    if response.method == "POST":
        product = response.POST.get("product")
        products = gi(product)
        return render(response, "MySite/scraper.html", {'products': products})
    else:
        return render(response, "MySite/scraper.html")

