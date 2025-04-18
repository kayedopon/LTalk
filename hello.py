import google.generativeai as genai
import PIL.Image # For loading images (install with: pip install Pillow)
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    print("Please set the GOOGLE_API_KEY in your .env file.")
    exit()

# Configure the API key
genai.configure(api_key=api_key)

# --- Configuration ---
# Make sure to set your GOOGLE_API_KEY environment variable
# Or configure it directly:
# genai.configure(api_key="YOUR_API_KEY")
# if not os.getenv('GOOGLE_API_KEY'):
#     print("Please set the GOOGLE_API_KEY environment variable.")
#     exit()
# else: # configure() is implicitly called if the env var is set
#     pass

image_path = "image.jpg" # Replace with your image path
prompt_text = "What is in this image? Describe it in detail."

# --- Load the Image ---
try:
    img = PIL.Image.open(image_path)
except FileNotFoundError:
    print(f"Error: Image file not found at {image_path}")
    exit()
except Exception as e:
    print(f"Error loading image: {e}")
    exit()

# --- Choose the Model ---
# Use a model that supports vision input
model = genai.GenerativeModel('gemini-1.5-pro-latest')
# Or for the newer models (check availability):
# model = genai.GenerativeModel('gemini-1.5-pro-latest')


# --- Make the API Request ---
print("Sending request to Gemini...")
try:
    # The SDK handles sending the image data correctly when you pass a PIL Image
    # It figures out the mime_type and base64 encoding internally.
    response = model.generate_content([prompt_text, img])

    # --- Process the Response ---
    print("\n--- Gemini Response ---")
    print(response.text)

except Exception as e:
    print(f"\nAn error occurred: {e}")
    # You might want to print response.prompt_feedback here for safety ratings etc.
    # print(response.prompt_feedback)

print("\n----------------------")
