import json
from django.shortcuts import render
import google.generativeai as genai
import PIL.Image
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

class TranslationResponse(BaseModel):
    words: list[dict[str, str]]  # Each word is a dictionary with 'original', 'infinitive', and 'translation'

def home(request):
    words = None
    error = None
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        try:
            img = PIL.Image.open(image_file)
            prompt_text = (
                "Look at the image, extract only Lithuanian words and provide their details. "
                "For each word, include the original Lithuanian word, its infinitive form, and its English translation. "
                "You act as an API agent, so you must not give me any additional comments."
            )
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[prompt_text, img],
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': TranslationResponse,
                },
            )
            try:
                parsed_response: TranslationResponse = response.parsed
                words = parsed_response.words
                print(words)
            except Exception as e:
                error = f"Failed to parse Gemini response: {e}"
        except Exception as e:
            error = f"Error: {e}"
    return render(request, 'main/home.html', {'words': words, 'error': error})