from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from .models import Word, WordSet, Exercise

import google.generativeai as genai
import PIL.Image
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise Exception("Please set the GOOGLE_API_KEY in your .env file.")

# Configure the API key
genai.configure(api_key=api_key)

# ...existing code...

prompt_text = ("Look at the image, extract only lithuanian words and give me their translation. "
               "Write original Lithuanian words in infinitive form. Format the response as a JSON array "
               "with objects containing 'word', 'translation', and 'infinitive' fields. "
               "Example format: [{\"word\":\"word\",\"translation\":\"translation\",\"infinitive\":\"infinitive\"}]")

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
    return render(request, "flashcard.html", context)