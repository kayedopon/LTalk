from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from django.shortcuts import get_object_or_404

from .serializer import ExerciseProgressSerializer, ExerciseSerializer, WordSerializer, WordSetSerializer, WordProgressSerializer
from main.models import Word, WordSet, WordProgress, Exercise, ExerciseProgress
from django.db import transaction

import google.generativeai as genai
import PIL.Image
from dotenv import load_dotenv
import os
import json


class WordViewSet(ModelViewSet):
   
    serializer_class = WordSerializer
    queryset = Word.objects.all()
    http_method_names = ['get', 'head', 'options']


class WordSetViewSet(ModelViewSet):

    serializer_class = WordSetSerializer
    queryset = WordSet.objects.all()


class WordProgressViewSet(ModelViewSet):

    serializer_class = WordProgressSerializer
    queryset = WordProgress.objects.all()
    http_method_names = ['get', 'head', 'options']


# ...existing code...

# ...existing code...
from main.models import Word, WordSet, WordProgress, Exercise, ExerciseProgress
# ...existing code...

class ExerciseViewSet(ModelViewSet):

    serializer_class = ExerciseSerializer
    queryset = Exercise.objects.all()
    # Allow POST for creation
    http_method_names = ['get', 'post', 'head', 'options']

    # Filter exercises by wordset and type if query parameters are provided
    def get_queryset(self):
        queryset = super().get_queryset()
        wordset_id = self.request.query_params.get('wordset')
        exercise_type = self.request.query_params.get('type')
        user = self.request.user # Get current user

        if wordset_id:
            queryset = queryset.filter(wordset_id=wordset_id)
        if exercise_type:
            queryset = queryset.filter(type=exercise_type)

        # Ensure only exercises belonging to the user's wordsets are returned
        queryset = queryset.filter(wordset__user=user)

        # If fetching flashcards, dynamically add filtered questions/answers
        if exercise_type == 'flashcard':
             for exercise in queryset:
                 filtered_words = self._get_unlearned_words(exercise.wordset, user)
                 questions, correct_answers = self._generate_flashcard_data(filtered_words)
                 # Attach dynamically generated data to the instance for the serializer to pick up
                 exercise.questions = questions
                 exercise.correct_answers = correct_answers

        return queryset

    def _get_unlearned_words(self, wordset, user):
        """Helper to get words not yet learned by the user."""
        all_words = wordset.words.all()
        if not all_words.exists():
            return Word.objects.none() # Return empty queryset if no words

        # Get progress for the user for words in this set
        progress_map = {
            wp.word_id: wp.is_learned
            for wp in WordProgress.objects.filter(user=user, word__in=all_words)
        }

        # Filter words: include if no progress exists or if progress shows not learned
        unlearned_word_ids = [
            word.id for word in all_words
            if progress_map.get(word.id, False) is False # Include if key not found (False) or value is False
        ]

        return all_words.filter(id__in=unlearned_word_ids)

    def _generate_flashcard_data(self, words):
        """Generates questions and answers dicts from a queryset of words."""
        questions = {}
        correct_answers = {}
        for i, word in enumerate(words):
            questions[str(i)] = {"front": word.word, "back": word.translation}
            correct_answers[str(i)] = word.translation
        return questions, correct_answers

    def _generate_fill_in_gap_data(self, words):
        """Generates fill-in-the-gap questions and answers"""
        questions = {}
        correct_answers = {}
        
        # No need for API key configuration here since it's done at module level
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        for i, word in enumerate(words):
            # Create a prompt to generate a Lithuanian sentence with a gap
            prompt = f"""
            Create a beginner-friendly sentence in Lithuanian using the word '{word.word}' (which means '{word.translation}' in English).
            It should be very clear from the context what the word is.
            The sentence should use this word in its proper grammatical form (not necessarily the basic form).
            For example, if the word is a noun, the sentence should use different case than the basic form.
            If the word is a verb, the sentence should use different tense or person than the basic form.
            Replace the word with a gap indicated by '___'.
            Format your response as a JSON object with the following structure:
            {{
                "sentence": "Example Lithuanian sentence with ___ (gap).",
                "correct_form": "correctWord"
            }}
            Do not add any explanation to your response.
            """
            
            try:
                response = model.generate_content(prompt)
                response_text = response.text.strip()
                
                # Extract the JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    sentence = data.get("sentence", "")
                    correct_form = data.get("correct_form", word.word)
                    
                    questions[str(i)] = {
                        "sentence": sentence,
                        "word": word.word,
                        "infinitive": word.infinitive,
                        "translation": word.translation
                    }
                    correct_answers[str(i)] = correct_form
                else:
                    # Fallback if JSON extraction fails
                    questions[str(i)] = {
                        "sentence": f"___ (using: {word.word}).",
                        "word": word.word,
                        "infinitive": word.infinitive,
                        "translation": word.translation
                    }
                    correct_answers[str(i)] = word.word
            except Exception as e:
                print(f"Error generating fill-in-gap question: {e}")
                # Fallback in case of error
                questions[str(i)] = {
                    "sentence": f"___ (using: {word.word}).",
                    "word": word.word,
                    "infinitive": word.infinitive,
                    "translation": word.translation
                }
                correct_answers[str(i)] = word.word
                
        return questions, correct_answers

    @transaction.atomic # Ensure atomicity
    def perform_create(self, serializer):
        wordset = serializer.validated_data['wordset']
        exercise_type = serializer.validated_data['type']
        user = self.request.user
        
        # For fill_in_gap exercises, we'll always generate fresh content
        # and avoid permanent database storage if possible
        if exercise_type == 'fill_in_gap':
            # Check if there's a timestamp in the request, which indicates
            # the user wants a fresh exercise
            has_timestamp = 'timestamp' in self.request.data
            
            # Get unlearned words for the current user
            unlearned_words = self._get_unlearned_words(wordset, user)
            
            # Generate fresh questions and answers
            questions, correct_answers = self._generate_fill_in_gap_data(unlearned_words)
            
            # Save as a temporary exercise (timestamp is already removed by serializer.create)
            instance = serializer.save(
                questions=questions,
                correct_answers=correct_answers
            )
            
            # If this is a timestamped request, we'll clean up old fill_in_gap exercises
            # to avoid database clutter (except for those with progress entries)
            if has_timestamp:
                # Find old fill_in_gap exercises without progress and delete them
                old_exercises = Exercise.objects.filter(
                    wordset__user=user,
                    type='fill_in_gap',
                    wordset=wordset
                ).exclude(
                    id=instance.id  # Don't delete the one we just created
                ).exclude(
                    progress_entries__isnull=False  # Don't delete exercises with progress
                )
                
                # Delete exercises older than a day (to avoid race conditions with active sessions)
                import datetime
                one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
                old_exercises.filter(id__lt=instance.id - 100).delete()
            
            return
            
        # For other exercise types (flashcard, etc.)    
        # Get only unlearned words for the current user
        unlearned_words = self._get_unlearned_words(wordset, user)
        
        # Generate questions/answers based on exercise type
        if exercise_type == 'flashcard' and 'questions' not in serializer.validated_data:
            questions, correct_answers = self._generate_flashcard_data(unlearned_words)
        else:
            # For other types or if questions are provided, use what's provided
            serializer.save()
            return

        # Save the exercise instance with the generated data
        serializer.save(
            questions=questions,
            correct_answers=correct_answers
        )
    

class SubmitExerciseAPIView(APIView):
    http_method_names = ['post', 'get']

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'user_answers': {
                        'type': 'object',
                        'description': 'A dictionary of user answers keyed by question identifier.',
                        'additionalProperties': {
                            'type': 'string',
                            'description': 'User\'s answer to a specific question.'
                        },
                        'example': {
                            "question_1": "Answer 1",
                            "question_2": "Answer 2"
                        }
                    }
                }
            }
        },
        responses={
            200: OpenApiResponse(
                response=ExerciseProgressSerializer,
                description="Returns exercise progress"
            ),
            400: OpenApiResponse(
                description="Bad Request, if 'user_answers' is missing"
            ),
        },
        description="Submit answers for an exercise"
    )

    def get(self, request, *args, **kwargs):
        expected_json = {
            "user_answers": {
                "1": "manzana",
                "2": "perro"
            }
        }
        return Response({
            "description": "This endpoint allows submitting exercise answers.",
            "expected_json": expected_json
        })

    def check_answer(self, user_answer, correct_answer, exercise_type):
        """Check if the user's answer matches the correct answer for the given exercise type"""
        
        if exercise_type == 'multiple_choice':
            if isinstance(correct_answer, list):
                return user_answer in correct_answer 
            else:
                return user_answer == correct_answer 
        
        elif exercise_type == 'flashcard':
            return user_answer == correct_answer
            
        elif exercise_type == 'fill_in_gap':
            # For fill-in-the-gap, we allow some flexibility in checking
            if not user_answer or not correct_answer:
                return False
            # Simple case-insensitive comparison for basic checking
            return user_answer.lower().strip() == correct_answer.lower().strip()
        
        return False
        
    def _generate_feedback(self, question_data, user_answer, correct_answer):
        """Generate feedback for incorrect answers using Gemini"""
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            sentence = question_data.get('sentence', '')
            word = question_data.get('word', '')
            infinitive = question_data.get('infinitive', '')
            translation = question_data.get('translation', '')
            
            prompt = f"""
            In a Lithuanian language learning exercise, the user was given this fill-in-the-gap sentence:
            '{sentence}'
            
            The word they needed to use is '{infinitive}' (infinitive form).
            The correct form to fill the gap is '{correct_answer}'.
            User answered: '{user_answer}'

            Please provide a helpful explanation (2-3 sentences) about:
            1. Why their answer is incorrect 
            2. What grammatical rules apply here
            3. How to correctly form this word from the infinitive

            Focus on Lithuanian grammar and word form. Be clear and educational.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating feedback: {e}")
            return f"The correct answer is '{correct_answer}'."

    def post(self, request, exercise_id):
        exercise = get_object_or_404(Exercise, id=exercise_id)
        user = request.user

        user_answers = request.data.get('user_answers')  
        if not user_answers:
            return Response({"error": "'user_answers' is required."}, status=status.HTTP_400_BAD_REQUEST)

        is_correct = True  
        correct = 0
        incorrect = 0
        feedback = {}
        
        related_words = exercise.wordset.words.all()
        
        # Determine if this is a partial submission (single answer) or a complete submission
        is_partial = len(user_answers) < len(exercise.questions)

        # Process only the submitted answers
        for key, user_answer in user_answers.items():
            if key not in exercise.questions:
                continue
                
            question_data = exercise.questions[key]
            correct_answer = exercise.correct_answers[key]
            question_is_correct = self.check_answer(user_answer, correct_answer, exercise.type)

            if question_is_correct:
                correct += 1
            else:
                incorrect += 1
                is_correct = False
                # Generate feedback for fill_in_gap exercises
                if exercise.type == 'fill_in_gap':
                    feedback[key] = self._generate_feedback(question_data, user_answer, correct_answer)

            # Find the word by matching either word or translation
            if exercise.type == 'fill_in_gap':
                word = related_words.filter(word__iexact=question_data.get('word', '')).first()
            else:
                word = related_words.filter(translation__iexact=correct_answer).first()
                
            if word:
                wp, _ = WordProgress.objects.get_or_create(user=user, word=word)
                wp.update_progress(question_is_correct)

        # Only create ExerciseProgress for complete submissions
        if not is_partial:
            progress = ExerciseProgress.objects.create(
                user=user,
                exercise=exercise,
                user_answer=user_answers,
                is_correct=is_correct,
                grade=f"{correct}/{correct + incorrect}" if (correct + incorrect) > 0 else "0/0"
            )
            response_data = {
                "exercise_progress": [ExerciseProgressSerializer(progress).data],
                "is_correct": is_correct,
                "feedback": feedback
            }
        else:
            # For partial submissions, just return feedback
            response_data = {
                "feedback": feedback
            }
            
        return Response(response_data, status=status.HTTP_200_OK)


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


class ProcessPhotoAPIView(APIView):
    http_method_names = ['post']
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Image file to process'
                    }
                }
            }
        },
        responses={
            200: OpenApiResponse(
                description="Returns extracted Lithuanian words",
                examples=[
                    {
                        "words": [
                            {"word": "obuolys", "translation": "apple", "infinitive": "obuolys"}
                        ]
                    }
                ]
            ),
            400: OpenApiResponse(description="Invalid image or bad format")
        },
        description="Extract Lithuanian words from an image"
    )
    def post(self, request):
        if 'image' not in request.FILES:
            return Response({"error": "No image file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['image']
        try:
            img = PIL.Image.open(file)
        except Exception as e:
            return Response({"error": f"Error loading image: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        model = genai.GenerativeModel('gemini-2.0-flash')
        try:
            response = model.generate_content([prompt_text, img])
            response_text = response.text.strip()

            if not response_text.startswith('['):
                import re
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(0)
                else:
                    return Response({
                        "error": "Invalid response format",
                        "raw_response": response_text
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            words_data = json.loads(response_text)
            if not isinstance(words_data, list):
                raise ValueError("Response is not a list")

            return Response({"words": words_data}, status=status.HTTP_200_OK)

        except json.JSONDecodeError as e:
            return Response({
                "error": "JSON parsing error",
                "message": str(e),
                "raw_response": response.text
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "error": "Processing error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



