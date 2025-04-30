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
        title = request.POST.get("wordset_title")
        description = request.POST.get("wordset_description")
        words_json = request.POST.get("words_json")

        if title and description and words_json:
            wordset = WordSet.objects.create(
                user=request.user,
                title=title,
                description=description
            )

            data = json.loads(words_json)
            for word in data:
                original = word["word"]
                infinitive = word["infinitive"]
                translation = word["translation"]

                word_obj, created = Word.objects.get_or_create(
                    word=original,
                    defaults={"infinitive": infinitive, "translation": translation}
                )
                wordset.words.add(word_obj)
            # Redirect to home after successful creation
            return redirect('home')
    return render(request, "create_set.html")

@require_http_methods(["POST"])
def photo_processing(request):
        if 'image' not in request.FILES:
            return HttpResponseBadRequest("No image file uploaded.")

        file = request.FILES['image']
        try:
            img = PIL.Image.open(file)
        except Exception as e:
            return HttpResponseBadRequest(f"Error loading image: {e}")

        model = genai.GenerativeModel('gemini-2.0-flash')
        try:
            response = model.generate_content([prompt_text, img])
            
            # Clean up the response text to ensure valid JSON
            response_text = response.text.strip()
            if not response_text.startswith('['):
                # If response isn't in expected JSON format, try to extract JSON portion
                import re
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(0)
                else:
                    # Create a structured error response
                    return JsonResponse({
                        "error": "Invalid response format",
                        "raw_response": response_text
                    }, status=500)

            # Parse the JSON response
            words_data = json.loads(response_text)
            
            # Validate the structure
            if not isinstance(words_data, list):
                raise ValueError("Response is not a list")
            
            # Return the processed data
            return JsonResponse({"words": words_data})

        except json.JSONDecodeError as e:
            return JsonResponse({
                "error": "JSON parsing error",
                "message": str(e),
                "raw_response": response.text
            }, status=500)
        except Exception as e:
            return JsonResponse({
                "error": "Processing error",
                "message": str(e)
            }, status=500)