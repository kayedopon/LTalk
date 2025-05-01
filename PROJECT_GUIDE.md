# Lithuanian Learning Django Project Guide

## 1. Project Overview
A web application for learning Lithuanian vocabulary. Users can:
- Register and log in with email and password.
- Upload images to extract Lithuanian words using Google Gemini AI.
- Create and manage word sets.
- Track progress on vocabulary and exercises.

## 2. Project Structure
```
LTalk/
├── LTalk/                # Django project settings, URLs, WSGI/ASGI
├── api/                  # REST API (DRF) for words, wordsets, exercises, image processing
├── authentication/       # Custom user model, registration, login/logout
├── main/                 # Main app: views, templates, static files
├── db.sqlite3            # SQLite database
├── requirements.txt      # Python dependencies
```

## 3. Authentication System
- **Custom User Model:** Uses email as the login field, with a custom manager for user creation.
- **Registration/Login:** Views and templates for user registration and login.
- **Session-based Auth:** Django’s session authentication is used for both web and API.

## 4. Main App: Word Sets and Home Page
- **Models:**
  - `WordSet`: A set of words, owned by a user.
  - `Word`: Lithuanian word, its infinitive, and translation.
  - `WordProgress`: Tracks user’s learning progress per word.
  - `Exercise`: Flashcard/multiple-choice exercises for a word set.
  - `ExerciseProgress`: Tracks user’s answers and grades for exercises.
- **Views:**
  - `home`: Shows all word sets for the logged-in user.
  - `create_set`: Lets users create a new word set, including via image upload.
- **Templates:**
  - `home.html`: Lists word sets, their word count, and progress.
  - `create_set.html`: Image upload and word set creation.
- **Static Files:**
  - CSS: `styles.css`
  - JS: `word_extractor.js`

## 5. Image Processing with Gemini AI
- User uploads an image on the create set page.
- JS sends the image to `/api/process-photo/`.
- The backend uses Google Gemini to extract Lithuanian words and their translations from the image.
- The response is a JSON array of `{word, translation, infinitive}` objects.
- JS displays the words and allows the user to edit/delete before creating a word set.

## 6. REST API (Django REST Framework)
- **Endpoints:**
  - `/api/word/`, `/api/wordset/`, `/api/wordprogress/`, `/api/exercise/`
  - `/api/exercise/<id>/submit/`: Submit answers for an exercise.
  - `/api/process-photo/`: Upload image and extract words.
- **Serializers:** Define how models are converted to/from JSON.
- **Permissions:** All API endpoints require authentication.

## 7. Frontend Logic (JavaScript)
- Handles file input, sends image to API, displays loading/error states.
- Renders extracted words as editable list.
- On submit, sends word set data to `/api/wordset/` via AJAX.
- Reads the CSRF token from cookies for POST requests.

## 8. Progress Tracking
- **Word Progress:** Each word tracks correct/incorrect attempts and whether it’s learned.
- **Exercise Progress:** Tracks user answers, correctness, and grades for each exercise.

## 9. Admin Interface
- Django admin is enabled for all models, with custom admin classes for better display and filtering.

## 10. Settings & Environment
- **Settings:**
  - Custom user model is set via `AUTH_USER_MODEL`.
  - Static files are served from `main/static/main/`.
  - REST Framework and drf-spectacular (for API docs) are configured.
- **Environment Variables:**
  - Google Gemini API key is loaded from `.env` using `python-dotenv`.

## 11. Testing
- Includes tests for registration, login, and logout.

## 12. How Everything Connects
1. User registers/logs in (custom user model, session auth).
2. Home page lists user’s word sets.
3. User uploads an image to extract Lithuanian words (Gemini AI).
4. JS displays extracted words; user can edit/delete.
5. User submits word set; data is sent to the API and saved.
6. User can practice with exercises; progress is tracked per word and exercise.

## 13. Extending the Project
- Add more exercise types.
- Add user profile and stats.
- Improve error handling and UI feedback.
- Add public/private sharing for word sets.

---

**Summary:**
This project is a full-stack Django app with custom authentication, REST API, and a modern JS frontend, leveraging Google Gemini for AI-powered word extraction from images. It’s modular, extensible, and well-structured for learning Lithuanian vocabulary.
