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

        if wordset_id:
            queryset = queryset.filter(wordset_id=wordset_id)
        if exercise_type:
            queryset = queryset.filter(type=exercise_type)

        # Ensure only exercises belonging to the user's wordsets are returned
        # (Assuming WordSet has a 'user' field)
        queryset = queryset.filter(wordset__user=self.request.user)
        return queryset

    @transaction.atomic # Ensure atomicity
    def perform_create(self, serializer):
        wordset = serializer.validated_data['wordset']
        exercise_type = serializer.validated_data['type']

        # Prevent creating duplicate exercises for the same wordset and type
        existing_exercise = Exercise.objects.filter(
            wordset=wordset,
            type=exercise_type
        ).first()

        if existing_exercise:
             # Instead of raising error, maybe return the existing one?
             # Or handle this in the serializer's validate method.
             # For now, let serializer handle potential duplicates if unique_together is set.
             # If not, this check prevents duplicates.
             # We'll let the serializer save if no exact duplicate found by filter.
             pass # Let serializer proceed, it might raise validation error if needed

        # Auto-generate questions/answers if not provided, specifically for flashcards
        if exercise_type == 'flashcard' and not serializer.validated_data.get('questions'):
            words = wordset.words.all()
            questions = {}
            correct_answers = {}
            for i, word in enumerate(words):
                questions[str(i)] = {"front": word.word, "back": word.translation}
                correct_answers[str(i)] = word.translation # Correct answer is the translation

            # Save generated data back to serializer instance
            serializer.instance = serializer.save(
                questions=questions,
                correct_answers=correct_answers
            )
        else:
             # For other types or if questions are provided, save normally
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

    def post(self, request, exercise_id):
        exercise = get_object_or_404(Exercise, id=exercise_id)
        user = request.user

        user_answers = request.data.get('user_answers')  
        if not user_answers:
            return Response({"error": "'user_answers' is required."}, status=status.HTTP_400_BAD_REQUEST)

       
        is_correct = True  
        correct = 0
        incorrect = 0
        
        related_words = exercise.wordset.words.all()

        for key, _ in exercise.questions.items():
            user_answer = user_answers.get(key)
            correct_answer = exercise.correct_answers[key]

            question_is_correct = self.check_answer(user_answer, correct_answer, exercise.type)

            
            if not question_is_correct:
                is_correct = False
                incorrect += 1
            else:
                correct += 1

            word = related_words.filter(translation__iexact=correct_answer).first()
            wp, _ = WordProgress.objects.get_or_create(user=user, word=word)

            if question_is_correct:
                wp.correct_attempts += 1
            else:
                wp.incorrect_attempts += 1

            wp.is_learned = wp.correct_attempts > wp.incorrect_attempts
            wp.save()

        progress = ExerciseProgress.objects.create(
            user=user,
            exercise=exercise,
            user_answer=user_answers,
            is_correct=is_correct,
            grade=f"{correct}/{correct + incorrect}" if (correct + incorrect) > 0 else "0/0"
        )
        return Response({
            "exercise_progress": [ExerciseProgressSerializer(progress).data],
            "is_correct": is_correct
        }, status=status.HTTP_200_OK)
        

    def check_answer(self, user_answer, correct_answer, exercise_type):
        """Check if the user's answer matches the correct answer for the given exercise type"""
        
        if exercise_type == 'multiple_choice':
            if isinstance(correct_answer, list):
                return user_answer in correct_answer 
            else:
                return user_answer == correct_answer 
        
        elif exercise_type == 'flashcard':
            return user_answer == correct_answer
        
        return False


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



