from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, TemplateView

from .models import StaticPage


class AboutView(TemplateView):
    template_name = "pages/about.html"


class RulesView(TemplateView):
    template_name = "pages/rules.html"


class StaticPageView(DetailView):
    model = StaticPage
    template_name = "pages/static_page.html"
    context_object_name = "page"
    queryset = StaticPage.objects.filter(is_published=True)

    def get_object(self, queryset=None):
        slug = self.kwargs.get("slug")
        return get_object_or_404(self.queryset, slug=slug)


def csrf_failure(request, reason=""):
    return render(request, "pages/403csrf.html", status=403)


def page_not_found(request, exception):
    return render(request, "pages/404.html", status=404)


def server_error(request):
    return render(request, "pages/500.html", status=500)


def registration(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("blog:index")
    else:
        form = UserCreationForm()

    return render(request, "registration/registration_form.html", {"form": form})
