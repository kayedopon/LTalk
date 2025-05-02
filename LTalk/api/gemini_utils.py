# filepath: c:\studies\vgtu\1_year\oop\LTalk\LTalk\LTalk\api\gemini_utils.py
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise Exception("Please set the GOOGLE_API_KEY in your .env file.")
genai.configure(api_key=api_key)

# Use a model suitable for text generation/understanding
# Consider 'gemini-1.5-flash-latest' or 'gemini-1.5-pro-latest' if available and needed
model = genai.GenerativeModel('gemini-2.0-flash') # Or a newer/more capable model

def generate_fill_in_gap_exercise(word: str):
    """
    Asks Gemini to create a sentence with a gap for the given Lithuanian word.
    Returns a dictionary {'sentence_template': '...', 'correct_form': '...'} or None on error.
    """
    prompt = (
        f"Create a Lithuanian sentence that uses the word '{word}' in a different or same grammatical form. "
        f"From the sentence it should be very clear which word to use lexically. Provide enough context"
        f"Do not change the part of the speeach of the word. If it was a noun, leave it as a noun, just change the declenation (accustaive, dative etc)"
        f"Replace the word in the sentence with '___' (three underscores). "
        f"Provide the original sentence with the word in the correct grammatical form. "
        f"Format the response as a JSON object with keys 'sentence_template' and 'correct_form'. "
        f"Example: {{ \"sentence_template\": \"Aš mėgstu ___\", \"correct_form\": \"obuolius\" }}."
        f"Only return the JSON object."
    )
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        # Basic JSON extraction (improve if needed)
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            data = json.loads(response_text[json_start:json_end])
            if 'sentence_template' in data and 'correct_form' in data:
                return data
        print(f"Warning: Could not parse Gemini response for sentence generation: {response_text}")
        return None
    except Exception as e:
        print(f"Error calling Gemini for sentence generation: {e}")
        return None

def get_gemini_explanation(sentence_template: str, correct_form: str, user_answer: str):
    """
    Asks Gemini to explain why the user_answer is incorrect for the given sentence.
    Returns the explanation string or None on error.
    """
    prompt = (
        f"In the Lithuanian sentence template \"{sentence_template}\", the correct word is '{correct_form}'. "
        f"A user answered '{user_answer}'. Explain briefly in simple terms why '{user_answer}' is incorrect "
        f"in this context. Focus on the grammatical reason (e.g., case, number). "
        f"Keep the explanation concise and suitable for a language learner. Start the explanation directly."
    )
    try:
        response = model.generate_content(prompt)
        # Add safety check if needed: response.prompt_feedback
        return response.text.strip()
    except Exception as e:
        print(f"Error calling Gemini for explanation: {e}")
        return None