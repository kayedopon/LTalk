from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login, password_validation
from .models import User


def registrationPage(request):
    page = "registration"
    
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == 'POST':
        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password1"]

        user = User.objects.filter(email=email)
        if len(user) == 0:
            user = User.objects.create_user(email=email, username=username, password=password)
            user = authenticate(request, email=email, password=password)
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

def logoutUser(request):
    logout(request)
    return redirect('login')



