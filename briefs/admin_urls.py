from django.urls import path

from . import views

app_name = "briefs_admin"

urlpatterns = [
    path("brief/<int:brief_id>/copy/", views.admin_copy_brief, name="admin_brief_copy"),
    path("brief/<int:brief_id>/progress/", views.admin_brief_progress, name="admin_brief_progress"),
    path("brief/choose-template/", views.admin_brief_choose_template, name="admin_brief_choose_template"),
    path(
        "brief/<int:brief_id>/create-from-template/",
        views.admin_create_from_template,
        name="admin_brief_create_from_template",
    ),
]
