from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/briefs/", include(("briefs.admin_urls", "briefs_admin"), namespace="briefs_admin")),
    path("admin/", admin.site.urls),
    path("brief/", include(("briefs.urls", "briefs"), namespace="briefs")),
    path("__reload__/", include("django_browser_reload.urls")),
    path("", RedirectView.as_view(pattern_name="admin:index", permanent=False)),
]
