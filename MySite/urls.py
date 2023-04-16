from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.index, name='index'),
    path('', views.index, name='index'),
    path('projects/', views.projects, name='projects'),
    path('scraper/', views.scraper, name='scraper'),
]