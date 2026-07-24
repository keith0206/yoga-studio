from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from django.urls import include, path


def health(_request):
    """Liveness for Fly HTTP checks — no DB, host-header safe via ALLOWED_HOSTS."""
    return HttpResponse("ok")


urlpatterns = [
    path("health/", health, name="health"),
    path("admin/", admin.site.urls),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("studio.urls")),
]
