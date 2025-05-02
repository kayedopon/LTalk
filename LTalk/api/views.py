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


# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise Exception("Please set the GOOGLE_API_KEY in your .env file.")

# Configure the API key
genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-2.0-flash')


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
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        queryset = super().get_queryset()
        wordset_id = self.request.query_params.get('wordset')
        exercise_type = self.request.query_params.get('type')
        user = self.request.user

        if wordset_id:
            queryset = queryset.filter(wordset_id=wordset_id)
        if exercise_type:
            queryset = queryset.filter(type=exercise_type)

        queryset = queryset.filter(wordset__user=user)

        if exercise_type == 'flashcard':
             for exercise in queryset:
                 filtered_words = self._get_unlearned_words(exercise.wordset, user)
                 questions, correct_answers = self._generate_flashcard_data(filtered_words)
                 exercise.questions = questions
                 exercise.correct_answers = correct_answers

        return queryset

    def _create_questions(self, data):
        prompt_text = (
            "Use the given list of Lithuanian words with their English translations to generate multiple choice questions. "
            "Each question should use the Lithuanian word as the question and provide four English answer options: "
            "one correct translation and three plausible but incorrect distractors. "
            "Format the response as a JSON array of objects with the following fields: "
            "'question' (Lithuanian word), 'choices' (list of 4 English answers), and 'correct' (correct English translation). "
            "Example format: ['1':{\"question\": \"eiti\", \"choices\": [\"to walk\", \"to sleep\", \"to eat\", \"to read\"], \"correct\": \"to walk\"}]\n\n"
            "Here is the list of words:\n"
        )

        word_list = [{"word": word.word, "translation": word.translation} for word in data]
        word_list_str = json.dumps(word_list, ensure_ascii=False, indent=2)

        full_prompt = prompt_text + word_list_str
        try:
            response = model.generate_content(full_prompt)
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

            questions = json.loads(response_text)
            if not isinstance(questions, list):
                raise ValueError("Response is not a list")

            return Response({"questions": questions}, status=status.HTTP_200_OK)

        except json.JSONDecodeError as e:
            return Response({
                "error": "JSON parsing error",
                "message": str(e),
                "raw_response": response.text
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_unlearned_words(self, wordset, user):
        """Helper to get words not yet learned by the user."""
        all_words = wordset.words.all()
        if not all_words.exists():
            return Word.objects.none() 

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
    
    @transaction.atomic # Ensure atomicity
    def perform_create(self, serializer):
        wordset = serializer.validated_data['wordset']
        exercise_type = serializer.validated_data['type']
        user = self.request.user

        existing_exercise = Exercise.objects.filter(
            wordset=wordset,
            type=exercise_type,
        )

        if not existing_exercise.exists():
            if exercise_type == 'flashcard' and 'questions' not in serializer.validated_data:
                # Get only unlearned words for the current user
                unlearned_words = self._get_unlearned_words(wordset, user)
                questions, correct_answers = self._generate_flashcard_data(unlearned_words)

                serializer.save(
                    questions=questions,
                    correct_answers=correct_answers
                )

            if exercise_type == 'multiple_choice' and not serializer.validated_data.get('questions'):
                words = wordset.words.all()
                response = self._create_questions(words)

                if response.status_code != 200:
                    raise Exception("Failed to generate questions")
                
                questions_list = response.data.get('questions', [])
                questions = {}
                correct_answers = {}

                for i, item in enumerate(questions_list):
                    questions[str(i)] = {
                        "question": item["question"],
                        "choices": item["choices"]
                    }
                    correct_answers[str(i)] = item["correct"]

                serializer.instance = serializer.save(
                    questions=questions,
                    correct_answers=correct_answers
                )
            else:
                serializer.save()
        else:
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

            if question_is_correct:
                correct += 1
            else:
                incorrect += 1
                is_correct = False

            word = related_words.filter(translation__iexact=correct_answer).first()
            wp, _ = WordProgress.objects.get_or_create(user=user, word=word)
            wp.update_progress(question_is_correct)

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



