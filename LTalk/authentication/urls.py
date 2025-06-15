from django.urls import path, include
from . import views
from allauth.socialaccount.providers.google.views import oauth2_login
urlpatterns = [
    path("login", views.loginPage, name="login"),
    path("registration", views.registrationPage, name="registration"),
    path("logout", views.logoutUser, name="logout"),
    path("google/login/", oauth2_login, name="google_login"),
    path('accounts/', include('allauth.urls')),  # Include all allauth URLs
]