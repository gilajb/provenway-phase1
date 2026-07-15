from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    path("interest/", views.InterestSignupCreateView.as_view(), name="interest-create"),
]
