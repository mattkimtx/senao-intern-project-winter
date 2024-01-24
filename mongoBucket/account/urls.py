from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "account"
urlpatterns = [
     path("", RedirectView.as_view(url="login/")),
     path("login/", views.login_view, name="login"),
     path("login/login_attempt/", views.login_attempt, name="login_attempt"),
     path("signup/", views.signup_view, name="signup"),
     path("signup/signup_attempt/", views.signup_attempt, name="signup_attempt"),
     path("logout/", views.logout_view, name="logout"),
]
