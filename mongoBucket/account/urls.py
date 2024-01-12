from django.urls import path
from . import views

app_name = "account"
urlpatterns = [
     path("", views.index, name="index"),
     path("login/", views.login, name="login"),
     path("login/login_attempt/", views.login_attempt, name="login_attempt"),
     path("signup/", views.signup, name="signup"),
     path("signup/signup_attempt/", views.signup_attempt, name="signup_attempt"),
]
