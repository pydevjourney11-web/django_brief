from django.urls import path

from . import views

app_name = "briefs"

urlpatterns = [
    path("<uuid:public_uuid>/", views.brief_fill, name="brief_fill"),
    path("<uuid:public_uuid>/autosave/", views.brief_autosave, name="brief_autosave"),
    path("<uuid:public_uuid>/submit/", views.brief_submit, name="brief_submit"),
]
