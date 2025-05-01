from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from .models import Word, WordSet

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
    return render(request, "home.html", {"wordsets": wordsets})

@login_required(login_url='login')
def create_set(request):
    if request.method == 'POST':
            return redirect('home')
    return render(request, "create_set.html")
