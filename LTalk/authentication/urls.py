from django.urls import path
from . import views
urlpatterns = [
    path("login", views.loginPage, name="login"),
    path("registration", views.registrationPage, name="registration"),
    path("logout", views.logoutUser, name="logout"),
]