from django.urls import path
from .views import add_book, search, get_book_details

urlpatterns = [
    path("add/", add_book),
    path("search/", search),
    path("search/details/", get_book_details),
]
