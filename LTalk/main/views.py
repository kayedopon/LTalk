from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import google.generativeai as genai
import PIL.Image
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

def home(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        try:
            img = PIL.Image.open(image_file)
            prompt_text = "Look at the image, extract only lithuanian words and give me their translation. Write original Lithuanian words in infinitive form. You act as an API agent, so you must not give me any additional comments. Answer in a JSON format"
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content([prompt_text, img])
            return render(request, 'main/home.html', {'result': response.text})
        except Exception as e:
            return render(request, 'main/home.html', {'result': f"Error: {e}"})
    return render(request, 'main/home.html')