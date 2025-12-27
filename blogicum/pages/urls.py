from django.urls import path

from .views import (
    AboutView,
    RulesView,
    StaticPageView,
    RegistrationView,
)

app_name = "pages"

urlpatterns = [
    path("about/", AboutView.as_view(), name="about"),
    path("rules/", RulesView.as_view(), name="rules"),
    path("page/<slug:slug>/", StaticPageView.as_view(), name="static_page"),
    path("auth/registration/", RegistrationView.as_view(), name="registration"),
]
