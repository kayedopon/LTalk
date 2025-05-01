from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from .models import Word, WordSet




@login_required(login_url='login')
def home(request):
    wordsets = WordSet.objects.filter(user=request.user)
    return render(request, "home.html", {"wordsets": wordsets})

@login_required(login_url='login')
def create_set(request):
    if request.method == 'POST':
            return redirect('home')
    return render(request, "create_set.html")


@login_required(login_url='login')
def wordset_detail(request, id):
    wordset = get_object_or_404(WordSet, pk=id)
    return render(request, 'wordset_detail.html', {'wordset': wordset})