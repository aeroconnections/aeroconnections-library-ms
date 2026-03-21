from django.urls import path

from . import views

app_name = "books"

urlpatterns = [
    path("books/", views.book_list, name="book_list"),
    path("books/new/", views.book_create, name="book_create"),
    path("books/<int:pk>/", views.book_detail, name="book_detail"),
    path("books/<int:pk>/edit/", views.book_edit, name="book_edit"),
    path("books/<int:pk>/delete/", views.book_delete, name="book_delete"),
    path("books/<int:book_pk>/copies/add/", views.copy_create, name="copy_create"),
    path("books/<int:book_pk>/copies/<int:copy_pk>/delete/", views.copy_delete, name="copy_delete"),
]
