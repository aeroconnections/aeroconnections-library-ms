from django.urls import path

from . import views

app_name = "loans"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("loans/", views.loan_list, name="loan_list"),
    path("loans/new/", views.loan_create, name="loan_create"),
    path("loans/<int:pk>/", views.loan_detail, name="loan_detail"),
    path("loans/<int:pk>/return/", views.loan_return, name="loan_return"),
    path("loans/<int:pk>/delete/", views.loan_delete, name="loan_delete"),
    path("return-notes/", views.return_notes, name="return_notes"),
    path("return-notes/<int:pk>/delete/", views.return_note_delete, name="return_note_delete"),
    path("activity-log/", views.activity_log, name="activity_log"),
]
