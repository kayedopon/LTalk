from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Value, DateTimeField
from django.db.models.functions import Coalesce, Greatest

from .models import WordSet, Exercise, WordProgress

import time
from datetime import datetime


@login_required(login_url='login')
def home(request):
    wordsets = WordSet.objects.filter(user=request.user).annotate(
            latest_exercise=Max('exercises__progress_entries__answered_at'),
            sort_time=Greatest(
                Coalesce(Max('exercises__progress_entries__answered_at'), Value(datetime.min, output_field=DateTimeField())),
                Coalesce('created', Value(datetime.min, output_field=DateTimeField()))
            )
    ).order_by('-sort_time')
    
    for ws in wordsets:
        ws.progress = ws.learned_percent(request.user)
    return render(request, "home.html", {"wordsets": wordsets})

@login_required(login_url='login')
def create_set(request):
    if request.method == 'POST':
            return redirect('home')
    return render(request, "create_set.html")

@login_required(login_url='login')
def flashcard_practice(request, wordset_id):
    wordset = get_object_or_404(WordSet, id=wordset_id, user=request.user)
    context = {
        'wordset': wordset,
        'wordset_id': wordset_id,
    }
    return render(request, "main/flashcard.html", context)

@login_required(login_url='login')
def fill_in_gap_practice(request, wordset_id):
    wordset = get_object_or_404(WordSet, id=wordset_id, user=request.user)
    # Add timestamp to ensure a new exercise is created each time
    timestamp = int(time.time())
    
    # The frontend JS will handle fetching/creating the exercise via the API
    context = {
        'wordset': wordset,
        'wordset_id': wordset_id, # Pass ID for JS
        'timestamp': timestamp, # Pass timestamp to ensure uniqueness
    }
    return render(request, "main/fill_in_gap.html", context)

@login_required(login_url='login')
def m_choice_practice(request, id):
    wordset = get_object_or_404(WordSet, id=id, user=request.user)

    context = {
        'wordset': wordset,
        'wordset_id': id,
    }
    return render(request, "m_choice.html", context)

@login_required(login_url='login')
def wordset_detail(request, id):
    wordset = get_object_or_404(WordSet, pk=id)
    if not wordset.public and wordset.user != request.user:
        return redirect('home')
    
    context = {
        'wordset': wordset,
        'user': request.user
    }
    return render(request, 'wordset_detail.html', context=context)

from collections import defaultdict

@login_required(login_url='login')
def exercise_history(request, id):
    wordset = get_object_or_404(WordSet, pk=id)
    exercises = wordset.exercises.prefetch_related('progress_entries')
    
    grouped_exercises = defaultdict(list)
    for exercise in exercises:
        grouped_exercises[exercise.type].append(exercise)

    context = {
        "wordset": wordset,
        "grouped_exercises": dict(grouped_exercises),
        "exercise_types": Exercise.EXERCISE_TYPES 
    }
    return render(request, 'exercise_history.html', context=context)

def explore_sets(request):
    return render(request, "explore_sets.html",)