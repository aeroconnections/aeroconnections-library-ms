from django.urls import path

from . import views

app_name = "borrowers"

urlpatterns = [
    path("", views.borrower_list, name="borrower_list"),
    path("create/", views.borrower_create, name="borrower_create"),
    path("import/", views.borrower_import, name="borrower_import"),
    path("import/confirm/", views.borrower_import_confirm, name="borrower_import_confirm"),
    path("<int:pk>/", views.borrower_detail, name="borrower_detail"),
    path("<int:pk>/edit/", views.borrower_edit, name="borrower_edit"),
    path("<int:pk>/deactivate/", views.borrower_deactivate, name="borrower_deactivate"),
    path("<int:pk>/reactivate/", views.borrower_reactivate, name="borrower_reactivate"),
]
