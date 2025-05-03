# Lithuanian Learning Django Project Guide

## 1. Project Overview
A web application for learning Lithuanian vocabulary. Users can:
- Register and log in with email and password.
- Upload images to extract Lithuanian words using Google Gemini AI.
- Create and manage word sets.
- Practice with multiple exercise types (flashcards, fill-in-the-gap, multiple choice).
- Track progress on vocabulary and exercises.

## 2. Project Structure
```
LTalk/
├── LTalk/                # Django project settings, URLs, WSGI/ASGI
├── api/                  # REST API (DRF) for words, wordsets, exercises, image processing
├── authentication/       # Custom user model, registration, login/logout
├── main/                 # Main app: views, templates, static files
├── staticfiles/          # Collected static files
├── db.sqlite3            # SQLite database
├── manage.py             # Django management script
```

## 3. Authentication System
- **Custom User Model:** Uses email as the login field, with a custom manager for user creation.
- **Registration/Login:** Views and templates for user registration and login.
- **Session-based Auth:** Django's session authentication is used for both web and API.

## 4. Main App: Word Sets and Home Page
- **Models:**
  - `WordSet`: A set of words, owned by a user, with public/private visibility.
  - `Word`: Lithuanian word, its infinitive, and translation.
  - `WordProgress`: Tracks user's learning progress per word.
  - `Exercise`: Flashcard/multiple-choice/fill-in-gap exercises for a word set.
  - `ExerciseProgress`: Tracks user's answers and grades for exercises.
  - `SentenceTemplate`: Provides example sentences for words.
- **Views:**
  - `home`: Shows all word sets for the logged-in user.
  - `create_set`: Lets users create a new word set, including via image upload.
  - `wordset_detail`: Shows details of a word set including its words.
  - `flashcard_practice`, `fill_in_gap_practice`, `m_choice_practice`: Different exercise types.
  - `exercise_history`: Shows history of exercises for a word set.
- **Templates:**
  - `home.html`: Lists word sets, their word count, and progress.
  - `create_set.html`: Image upload and word set creation.
  - `wordset_detail.html`: Shows details of a word set and its words.
  - Exercise-specific templates for each practice type.
- **Static Files:**
  - CSS: `styles.css`
  - JS: `word_extractor.js` and exercise-specific scripts

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
- **Documentation:** API schema and documentation available via drf-spectacular.

## 7. Frontend Logic (JavaScript)
- Handles file input, sends image to API, displays loading/error states.
- Renders extracted words as editable list.
- On submit, sends word set data to `/api/wordset/` via AJAX.
- Reads the CSRF token from cookies for POST requests.
- Exercise-specific JS handles the interactive aspects of each exercise type.

## 8. Progress Tracking
- **Word Progress:** Each word tracks correct/incorrect attempts and whether it's learned.
  - A word is considered learned after 3 correct attempts with at least 60% accuracy.
- **Exercise Progress:** Tracks user answers, correctness, and grades for each exercise.
- Progress visualization is shown on the home page and exercise history.

## 9. Exercise Types
- **Flashcards:** Traditional flashcard study with word/translation pairs.
- **Fill in the Gap:** Users complete sentences with the correct form of words.
- **Multiple Choice:** Users select the correct translation from options.
- Each exercise type has its own template and JavaScript logic.

## 10. Admin Interface
- Django admin is enabled for all models, with custom admin classes for better display and filtering.

## 11. Settings & Environment
- **Settings:**
  - Custom user model is set via `AUTH_USER_MODEL`.
  - Static files are served from `main/static/main/`.
  - REST Framework and drf-spectacular (for API docs) are configured.
- **Environment Variables:**
  - Google Gemini API key is loaded from `.env` using `python-dotenv`.

## 12. Testing
- Includes tests for registration, login, and logout.
- Model tests verify the functionality of the core models.

## 13. How Everything Connects
1. User registers/logs in (custom user model, session auth).
2. Home page lists user's word sets.
3. User uploads an image to extract Lithuanian words (Gemini AI).
4. JS displays extracted words; user can edit/delete.
5. User submits word set; data is sent to the API and saved.
6. User can practice with different exercise types; progress is tracked per word and exercise.
7. User can view their exercise history and word learning progress.

## 14. Recent Updates
- Added public/private sharing for word sets.
- Enhanced word detail view with more context.
- Added sentence templates for fill-in-the-gap exercises.
- Improved progress tracking and visualization.
- Added exercise history view.

---

**Summary:**
This project is a full-stack Django app with custom authentication, REST API, and a modern JS frontend, leveraging Google Gemini for AI-powered word extraction from images. The application offers multiple exercise types and comprehensive progress tracking to help users effectively learn Lithuanian vocabulary.
