from django.urls import path

from .views import (
    AboutView,
    RulesView,
    StaticPageView,
    csrf_failure,
    page_not_found,
    registration,
    server_error,
)

app_name = "pages"

urlpatterns = [
    path("about/", AboutView.as_view(), name="about"),
    path("rules/", RulesView.as_view(), name="rules"),
    path("page/<slug:slug>/", StaticPageView.as_view(), name="static_page"),
    path("auth/registration/", registration, name="registration"),
    path("test/403/", csrf_failure, name="test_403"),
    path("test/404/", page_not_found, name="test_404"),
    path("test/500/", server_error, name="test_500"),
]
