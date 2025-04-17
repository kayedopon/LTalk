from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from .models import User

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
        email = request.POST["email"]
        username = request.POST["username"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if clean_passwords(request, password1, password2):
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(email=email, username=username, password=password1)
                user = authenticate(request, email=email, password=password1)
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "User already exist")

    context = {"page": page, "title": page.title()}
    return render(request, "auth/registration.html", context=context)


def loginPage(request):
    page = "login"

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == 'POST':
        email = request.POST["email"]
        password = request.POST["password"]
        print(email)
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Wrong password')
        except:
            messages.error(request, "User does not exist")

    context = {"page": page, "title": page.title()}
    return render(request, "auth/login.html", context=context)

@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('login')



