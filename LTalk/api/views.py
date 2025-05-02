from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status, serializers

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
from random import sample
from .gemini_utils import generate_fill_in_gap_exercise, get_gemini_explanation # Import helpers
from django.db import models


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
        # Note: This modifies the queryset objects *before* serialization.
        # This approach might be less clean than modifying the serializer's representation.
        # Consider modifying the serializer or list/retrieve methods for a cleaner separation.
        if exercise_type == 'flashcard':
             for exercise in queryset:
                 filtered_words = self._get_unlearned_words(exercise.wordset, user)
                 questions, correct_answers = self._generate_flashcard_data(filtered_words)
                 # Attach dynamically generated data to the instance for the serializer to pick up
                 # This assumes the serializer fields are not read_only for this purpose.
                 # If they are read_only, this won't work directly.
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

    def _generate_fill_in_gap_data(self, wordset, num_questions=5):
        """Generates questions and answers for fill-in-the-gap."""
        words = list(wordset.words.all())
        if not words:
            return {}, {}

        # Select a sample of words
        selected_words = sample(words, min(len(words), num_questions))

        questions = {}
        correct_answers = {}
        q_index = 1
        for word in selected_words:
            generated_data = generate_fill_in_gap_exercise(word.infinitive)
            if generated_data:
                q_key = str(q_index)
                questions[q_key] = {"sentence_template": generated_data['sentence_template']}
                correct_answers[q_key] = generated_data['correct_form']
                q_index += 1

        return questions, correct_answers

    @transaction.atomic
    def perform_create(self, serializer):
        wordset = serializer.validated_data['wordset']
        exercise_type = serializer.validated_data['type']
        user = self.request.user # Needed for potential future use

        # Prevent creating duplicates if an exercise of the same type exists? Optional.
        # existing_exercise = Exercise.objects.filter(wordset=wordset, type=exercise_type).first()
        # if existing_exercise:
        #     # Return existing or raise error? Depends on desired behavior.
        #     # For now, allow multiple exercises of the same type.
        #     pass

        questions = serializer.validated_data.get('questions')
        correct_answers = serializer.validated_data.get('correct_answers')

        # Generate data if not provided and type requires it
        if exercise_type == 'flashcard' and not questions:
            # Generate flashcard data (using existing or adapted logic)
            # Assuming _get_unlearned_words and _generate_flashcard_data exist
            unlearned_words = self._get_unlearned_words(wordset, user)
            questions, correct_answers = self._generate_flashcard_data(unlearned_words)
            serializer.save(questions=questions, correct_answers=correct_answers)

        elif exercise_type == 'fill_in_the_gap' and not questions:
            # Generate fill-in-the-gap data
            questions, correct_answers = self._generate_fill_in_gap_data(wordset)
            if not questions: # Handle case where generation failed or no words
                 raise serializers.ValidationError("Could not generate fill-in-the-gap questions for this wordset.")
            serializer.save(questions=questions, correct_answers=correct_answers)

        else:
            # Save normally if data was provided or type doesn't need generation
            serializer.save()
    

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
                            'description': 'User’s answer to a specific question.'
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

    @transaction.atomic # Wrap in transaction
    def post(self, request, exercise_id):
        exercise = get_object_or_404(Exercise, id=exercise_id)
        user = request.user
        user_answers_dict = request.data.get('user_answers') # Expecting {'q_key': 'answer'}

        if not user_answers_dict or not isinstance(user_answers_dict, dict):
            return Response({"error": "'user_answers' must be a dictionary."}, status=status.HTTP_400_BAD_REQUEST)

        overall_correct = True
        total_questions = len(exercise.questions)
        correct_count = 0
        progress_entries = [] # Store progress entries to return

        # Use prefetch_related for efficiency if accessing wordset.words often
        exercise = Exercise.objects.prefetch_related('wordset__words').get(id=exercise_id)
        word_map = {w.infinitive: w for w in exercise.wordset.words.all()} # Map for easier lookup if needed

        for q_key, question_data in exercise.questions.items():
            user_answer = user_answers_dict.get(q_key)
            correct_answer = exercise.correct_answers.get(q_key)
            explanation = None # Reset explanation for this question

            if user_answer is None or correct_answer is None:
                # Handle missing answer or question data - maybe skip or mark incorrect
                question_is_correct = False
                overall_correct = False
                # explanation = "Question data missing or answer not provided." # Keep explanation None here
            else:
                question_is_correct = self.check_answer(user_answer, correct_answer, exercise.type)

                if question_is_correct:
                    correct_count += 1
                else:
                    overall_correct = False
                    # Get explanation only if incorrect and it's fill_in_the_gap
                    if exercise.type == 'fill_in_the_gap':
                         sentence_template = question_data.get('sentence_template', '')
                         # Ensure all required args are passed to get_gemini_explanation
                         explanation = get_gemini_explanation(sentence_template, correct_answer, user_answer)
                         last_explanation = explanation # Store the most recent explanation
            related_word = None
            if correct_answer: # Only proceed if we have a correct answer to look up
                possible_words = exercise.wordset.words.filter(
                    models.Q(translation__iexact=correct_answer) |
                    models.Q(infinitive__iexact=correct_answer) |
                    models.Q(word__iexact=correct_answer)
                )
                if possible_words.exists():
                    related_word = possible_words.first()

            if related_word:
                wp, _ = WordProgress.objects.get_or_create(user=user, word=related_word, defaults={'user': user, 'word': related_word})
                wp.update_progress(question_is_correct) # Use the method from WordProgress model
            else:
                # Avoid printing excessive warnings if correct_answer was None initially
                if correct_answer:
                    print(f"Warning: Could not find related Word for answer '{correct_answer}' in exercise {exercise.id}, question key {q_key}")
            # --- End WordProgress Update ---

        # <<< --- ADD THIS MISSING CODE --- >>>
        # Create a single ExerciseProgress entry for the entire submission attempt
        progress = ExerciseProgress.objects.create(
            user=user,
            exercise=exercise,
            user_answer=user_answers_dict, # Store all answers submitted
            is_correct=overall_correct,
            grade=f"{correct_count}/{total_questions}" if total_questions > 0 else "0/0",
            # Store the last explanation generated if the overall result was incorrect
            explanation=last_explanation if not overall_correct else None
        )
        progress_entries.append(progress)

        # Return the list of progress entries (currently just one)
        return Response({
            "exercise_progress": ExerciseProgressSerializer(progress_entries, many=True).data,
            "overall_correct": overall_correct # Indicate if the whole attempt was correct
        }, status=status.HTTP_200_OK)

    def check_answer(self, user_answer, correct_answer, exercise_type):
        """Check if the user's answer matches the correct answer."""
        # Normalize answers (lowercase, strip whitespace) for comparison
        user_answer_norm = str(user_answer).strip().lower() if user_answer is not None else ""
        correct_answer_norm = str(correct_answer).strip().lower()

        if exercise_type == 'multiple_choice':
            # Assuming correct_answer could be a list or single value
            if isinstance(correct_answer, list):
                return user_answer_norm in [str(ca).strip().lower() for ca in correct_answer]
            else:
                return user_answer_norm == correct_answer_norm
        elif exercise_type == 'flashcard':
             # Flashcard 'correct' button means user_answer matches correct_answer implicitly
             # The submitted user_answer for 'correct' should be the correct_answer itself.
             return user_answer_norm == correct_answer_norm
        elif exercise_type == 'fill_in_the_gap':
             # Direct comparison for fill-in-the-gap
             return user_answer_norm == correct_answer_norm

        return False


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



