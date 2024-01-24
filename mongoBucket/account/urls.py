from django.urls import path
from . import views

app_name = "account"
urlpatterns = [
     path("", views.loginPage.as_view(), name="loginPage"),
     path("login/", views.login, name="login"),
     path("signup/", views.signup, name="signup"),
]
