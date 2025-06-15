from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from .models import User
from django.core.exceptions import ValidationError 
from axes.utils import reset_request
from django.urls import reverse
import logging

from LTalk.settings import LANGUAGE_CHOICES


auth_logger = logging.getLogger('authentication')

def clean_passwords(request, ps1, ps2):
    if ps1 and ps2:
        if ps1 != ps2:
            messages.error(request, "Passwords do not match.") 
            return False
    return True

def registrationPage(request):
    page = "registration"
    
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == 'POST':
        if all(k in request.POST for k in ["email", "username", "password1", "password2"]):
            email = request.POST["email"]
            username = request.POST["username"]
            password1 = request.POST["password1"]
            password2 = request.POST["password2"]
            selected_language = request.POST.get('language')
            print(selected_language)
            if clean_passwords(request, password1, password2):
                if not User.objects.filter(email=email).exists():
                    try:
                        # This will run ALL validators in AUTH_PASSWORD_VALIDATORS
                        validate_password(password1)
                        # Only create user if password validation passes
                        user = User.objects.create_user(email=email, username=username, password=password1, language=selected_language)
                        user = authenticate(request, email=email, password=password1)
                        login(request, user)
                        return redirect("home")
                    except ValidationError as error:
                        for message in error.messages:
                            messages.error(request, message)
                else:
                    messages.error(request, "User already exist")
        else:
            messages.error(request, "You need to fill all fields")

    context = {"page": page, "title": page.title(), "lang_choices": LANGUAGE_CHOICES}
    return render(request, "auth/registration.html", context=context)


def loginPage(request):
    page = "login"

    if request.user.is_authenticated:
        return redirect("home")
    
    if request.GET.get('lockout') == 'true':
        messages.error(request, "Too many failed login attempts. Please try again later")

    if request.GET.get('csrf_error') == 'true':
        messages.error(request, "Security token validation failed. Please try again.")

    if request.method == 'POST':
        if all(k in request.POST for k in ["email", "password"]):
            email = request.POST["email"]
            password = request.POST["password"]
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, email=email, password=password)

                if user is not None:
                    login(request, user)
                    auth_logger.info(f"Successful login: {email} from IP {request.META.get('REMOTE_ADDR')}")
                    return redirect('home')
                else:
                    auth_logger.warning(f"Failed login attempt: {email} from IP {request.META.get('REMOTE_ADDR')} - Invalid password")
                    messages.error(request, 'Wrong password')
            except:
                auth_logger.warning(f"Failed login attempt: {email} from IP {request.META.get('REMOTE_ADDR')} - User does not exist")
                messages.error(request, "User does not exist")
        else:
            auth_logger.warning(f"Failed login attempt from IP {request.META.get('REMOTE_ADDR')} - Missing fields")
            messages.error(request, "You need to fill all fields")

    context = {"page": page, "title": page.title()}
    return render(request, "auth/login.html", context=context)

def axes_lockout_handler(request, credentials=None, *args, **kwargs):
    """Custom lockout handler that adds a message and redirects to login"""
    # Log the lockout attempt
    auth_logger.warning(f"Account locked: IP {request.META.get('REMOTE_ADDR')} - Too many failed login attempts")
    
    # Get the base URL first, then add the query parameter
    base_url = reverse('login')
    return redirect(f"{base_url}?lockout=true")

def csrf_failure(request, reason=""):
    """Custom CSRF failure view that logs the failure and redirects to login with error message"""
    # Log the CSRF failure attempt
    auth_logger.warning(
        f"CSRF validation failed: {reason} - IP: {request.META.get('REMOTE_ADDR')} - Path: {request.path}",
        extra={
            'remote_addr': request.META.get('REMOTE_ADDR', 'unknown'),
            'user': 'anonymous'  # CSRF failures typically happen before authentication
        }
    )
    
    # Redirect to login page with csrf error parameter
    return redirect(f"{reverse('login')}?csrf_error=true")

@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('login')



