from django.urls import path
from . import views

app_name = "selectApp"
urlpatterns = [
    path("", views.index, name="index"),
    path("query/", views.query, name="query"),
    path("query/delete/", views.delete, name="delete"),
]
