from django.urls import path
from .views import add_book, search

urlpatterns = [
    path("add/", add_book),
    path("search/", search),
]
