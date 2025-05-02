from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Word, WordSet, Exercise, WordProgress

import google.generativeai as genai
import PIL.Image
from dotenv import load_dotenv
import os
import json
import time

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise Exception("Please set the GOOGLE_API_KEY in your .env file.")

# Configure the API key
genai.configure(api_key=api_key)

# ...existing code...

# prompt = (
#     "Look at the image, extract only Lithuanian words and give me their English translation. "
#     "For each word, return: "
#     "- the original word exactly as it appears, "
#     "- its English translation, "
#     "- and its basic form (lemma), without changing the part of speech. "
#     "IMPORTANT: The field name 'infinitive' is just a label and DOES NOT mean the word must be a verb. "
#     "For nouns, return the nominative singular form in the 'infinitive' field. "
#     "For verbs, return the actual infinitive form. "
#     "For adjectives, use the masculine nominative singular form, and for other parts of speech, use the dictionary base form. "
#     "Do NOT convert nouns into verbs. For example, do NOT convert 'stalas' (a noun) into 'stalauti' (a verb). "
#     "Preserve the original part of speech. "
#     "Format the output as a JSON array of objects with the following fields: "
#     "'word' (original form), 'translation' (English meaning), and 'infinitive' (basic form). "
#     "Example: [{\"word\": \"stalo\", \"translation\": \"table\", \"infinitive\": \"stalas\"}, "
#     "{\"word\": \"eina\", \"translation\": \"goes\", \"infinitive\": \"eiti\"}]"
# )


@login_required(login_url='login')
def home(request):
    wordsets = WordSet.objects.filter(user=request.user)
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
    # We don't necessarily need to fetch the Exercise here,
    # the frontend JS will handle fetching/creating it via the API.
    context = {
        'wordset': wordset,
        'wordset_id': wordset_id, # Pass ID for JS
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
def wordset_detail(request, id):
    wordset = get_object_or_404(WordSet, pk=id)
    return render(request, 'wordset_detail.html', {'wordset': wordset})

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

@login_required(login_url='login')
def delete_wordset(request, id):
    wordset = get_object_or_404(WordSet, pk=id, user=request.user)
    if request.method == 'POST':
        # For each word in the set
        for word in wordset.words.all():
            if word.wordsets.count() == 1:  # Only in this set
                # Delete all progress for this word
                WordProgress.objects.filter(word=word).delete()
                # Remove the word itself
                word.delete()
            else:
                # Just remove the relation
                word.wordsets.remove(wordset)
        wordset.delete()
        return redirect('home')
    return render(request, 'confirm_delete.html', {'wordset': wordset})