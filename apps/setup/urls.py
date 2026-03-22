from django.urls import path

from .views import SetupCompleteView, SetupGateView, SetupSecurityView, SetupWizardView

app_name = "setup"

urlpatterns = [
    path("", SetupGateView.as_view(), name="gate"),
    path("wizard/", SetupWizardView.as_view(), name="wizard"),
    path("security/", SetupSecurityView.as_view(), name="security"),
    path("complete/", SetupCompleteView.as_view(), name="complete"),
]
