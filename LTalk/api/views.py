from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from django.shortcuts import get_object_or_404
from django.db.models import Max, Value, DateTimeField
from django.db.models.functions import Coalesce, Greatest

from .serializer import ExerciseProgressSerializer, ExerciseSerializer, WordSerializer, WordSetSerializer, WordProgressSerializer
from main.models import Word, WordSet, WordProgress, Exercise, ExerciseProgress
from django.db import transaction

import google.generativeai as genai
import PIL.Image
from dotenv import load_dotenv
import os
import json
from datetime import datetime


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
    http_method_names = ['get', 'post', 'patch', 'head', 'options', 'delete']
    
    def get_queryset(self):
        scope = self.request.query_params.get("scope")
        search = self.request.query_params.get("search", "").strip()

        queryset = WordSet.objects.all()


        if scope == 'others':
            queryset = queryset.filter(public=True).exclude(user=self.request.user)
            if search:
                return queryset.filter(title__icontains=search).order_by('-created')
            return queryset.order_by('-created')

        return queryset.filter(user=self.request.user).annotate(
            latest_exercise=Max('exercises__progress_entries__answered_at'),
            sort_time=Greatest(
                Coalesce(Max('exercises__progress_entries__answered_at'), Value(datetime.min, output_field=DateTimeField())),
                Coalesce('created', Value(datetime.min, output_field=DateTimeField()))
            )
        ).order_by('-sort_time')
    
    @action(detail=True, methods=['post'], url_path='duplicate')
    def duplicate_wordset(self, request, pk=None):
        original = WordSet.objects.filter(pk=pk).first()

        if not original.public:
            return Response({"error": "This word set is private."}, status=status.HTTP_403_FORBIDDEN)

        # Prevent multiple duplications
        already_duplicated = WordSet.objects.filter(user=request.user, duplicated_from=original).exists()
        if already_duplicated:
            return Response(
                {"error": "You have already duplicated this word set."},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_wordset = WordSet.objects.create(
            user=request.user,
            title=original.title,
            description=original.description,
            public=False,
            duplicated_from=original
        )

        new_wordset.words.set(original.words.all())

        serializer = self.get_serializer(new_wordset)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        wordset = get_object_or_404(WordSet, pk=pk, user=request.user)

        for word in wordset.words.all():
            if word.wordsets.count() == 1:
                WordProgress.objects.filter(word=word).delete()
                word.delete()
            else:
                word.wordsets.remove(wordset)

        wordset.delete()
        return Response({"detail": "Word set deleted."}, status=status.HTTP_204_NO_CONTENT)


class WordProgressViewSet(ModelViewSet):

    serializer_class = WordProgressSerializer
    queryset = WordProgress.objects.all()
    http_method_names = ['get', 'head', 'options']

    def get_queryset(self):
        return WordProgress.objects.filter(user=self.request.user)




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

        elif exercise_type == "multiple_choice":
            for exercise in queryset:
                questions, correct_answers = self._generate_m_choice_data(exercise.wordset.words.all())
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
            if word.id not in progress_map or progress_map[word.id] is False
        ]

        # If no unlearned words but there are words in the set, return all words
        if not unlearned_word_ids and all_words.exists():
            return all_words
        
        return all_words.filter(id__in=unlearned_word_ids)

    def _generate_flashcard_data(self, words):
        """Generates questions and answers dicts from a queryset of words."""
        questions = {}
        correct_answers = {}
        for i, word in enumerate(words):
            questions[str(i)] = {"front": word.word, "back": word.translation}
            correct_answers[str(i)] = word.translation
        return questions, correct_answers

    def _generate_m_choice_data(self, words):
        """Generates questions and answers dicts from a queryset of words."""
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
        return questions, correct_answers
    # Replace the _generate_fill_in_gap_data method in ExerciseViewSet in LTalk/api/views.py:

    def _generate_fill_in_gap_data(self, words):
        """Generates fill-in-the-gap questions and answers with rate limiting"""
        questions = {}
        correct_answers = {}
        
        from main.models import SentenceTemplate
        import time
        import random
        from datetime import datetime, timedelta
        
        # Rate limiting management
        MAX_CALLS_PER_MINUTE = 15
        SAFE_LIMIT = 12  # Stay a bit under the limit for safety
        
        # Keep track of API calls with timestamps
        if not hasattr(self.__class__, '_api_call_timestamps'):
            self.__class__._api_call_timestamps = []
        
        # Clean up old timestamps (older than 1 minute)
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        self.__class__._api_call_timestamps = [
            ts for ts in self.__class__._api_call_timestamps 
            if ts > one_minute_ago
        ]
        
        # Count recent API calls (within the last minute)
        recent_calls = len(self.__class__._api_call_timestamps)
        
        for i, word in enumerate(words):
            # Check if we're approaching the rate limit
            approaching_limit = recent_calls >= SAFE_LIMIT
            
            if approaching_limit:
                # We're close to the rate limit, use a stored template if available
                templates = SentenceTemplate.objects.filter(word=word)
                
                if templates.exists():
                    # Use a stored template
                    template = random.choice(list(templates))
                    
                    questions[str(i)] = {
                        "sentence": template.sentence,
                        "word": word.word,
                        "infinitive": word.infinitive,
                        "translation": word.translation
                    }
                    correct_answers[str(i)] = template.correct_form
                    
                    print(f"Using stored template for '{word.word}' (rate limit approaching)")
                    continue
                
                # If no template is available and we're at the limit, wait
                if recent_calls >= MAX_CALLS_PER_MINUTE:
                    # Calculate how long to wait
                    oldest_call = min(self.__class__._api_call_timestamps)
                    wait_time = 60 - (now - oldest_call).total_seconds()
                    if wait_time > 0:
                        print(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                        time.sleep(wait_time + 1)  # Add 1 second buffer
                    
                    # Reset recent calls counter
                    self.__class__._api_call_timestamps = []
                    recent_calls = 0
            
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            prompt = f"""
            Create a beginner-friendly, complete Lithuanian sentence using the word '{word.word}' (which means '{word.translation}' in English).
            - The sentence must be clear and understandable, with enough context for a language learner.
            - Use the word in a grammatically correct, but not basic, form (e.g., different case for nouns, different tense/person for verbs).
            - Replace the word with a gap indicated by '___'.
            - Do NOT return an empty or placeholder sentence.
            - Do NOT return only the word or a fragment.
            - Example output:
            {{
                "sentence": "Man patinka keliauti su ___ per upę.",
                "correct_form": "keltu"
            }}
            Format your response as a JSON object with the fields 'sentence' and 'correct_form'. Do not add any explanation.
            """
            
            try:
                response = model.generate_content(prompt)
                response_text = response.text.strip()
                
                # Record this API call for rate limiting
                self.__class__._api_call_timestamps.append(datetime.now())
                recent_calls += 1
                
                # Extract the JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    sentence = data.get("sentence", "")
                    correct_form = data.get("correct_form", word.word)
                    
                    # Store or update the template for future fallback
                    if sentence and sentence != f"___ (using: {word.word}).":
                        SentenceTemplate.objects.update_or_create(
                            word=word,
                            defaults={
                                'sentence': sentence,
                                'correct_form': correct_form
                            }
                        )
                    
                    questions[str(i)] = {
                        "sentence": sentence,
                        "word": word.word,
                        "infinitive": word.infinitive,
                        "translation": word.translation
                    }
                    correct_answers[str(i)] = correct_form
                else:
                    # JSON extraction failed, check for fallback from database
                    template = SentenceTemplate.objects.filter(word=word).first()
                    
                    if template:
                        # Use stored template as fallback
                        questions[str(i)] = {
                            "sentence": template.sentence,
                            "word": word.word,
                            "infinitive": word.infinitive,
                            "translation": word.translation
                        }
                        correct_answers[str(i)] = template.correct_form
                        print(f"Using stored template for '{word.word}' (parsing failed)")
                    else:
                        # No stored template, use basic fallback
                        questions[str(i)] = {
                            "sentence": f"___ (using: {word.word}).",
                            "word": word.word,
                            "infinitive": word.infinitive,
                            "translation": word.translation
                        }
                        correct_answers[str(i)] = word.word
            except Exception as e:
                print(f"Error generating fill-in-gap question for '{word.word}': {e}")
                
                # Error occurred, check for fallback from database
                template = SentenceTemplate.objects.filter(word=word).first()
                
                if template:
                    # Use stored template as fallback
                    questions[str(i)] = {
                        "sentence": template.sentence, 
                        "word": word.word,
                        "infinitive": word.infinitive,
                        "translation": word.translation
                    }
                    correct_answers[str(i)] = template.correct_form
                    print(f"Using stored template for '{word.word}' (API error)")
                else:
                    # No stored template, use basic fallback
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
            
            # If no unlearned words found, use all words in the set
            if not unlearned_words.exists() and wordset.words.exists():
                unlearned_words = wordset.words.all()
            
            # Limit number of words to avoid rate limit issues
            MAX_WORDS_PER_REQUEST = 12  # Adjust based on your needs - well under the 15/min limit
            limited_words = list(unlearned_words)[:MAX_WORDS_PER_REQUEST]
            
            # If we still have no words, create a basic empty structure
            if not limited_words:
                questions = {"0": {"sentence": "No words available in this set."}}
                correct_answers = {"0": ""}
            else:
                # Generate fresh questions and answers
                questions, correct_answers = self._generate_fill_in_gap_data(limited_words)
            
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
        
        # If no unlearned words found, use all words in the set
        if not unlearned_words.exists() and wordset.words.exists():
            unlearned_words = wordset.words.all()
        
        # Generate questions/answers based on exercise type
        if exercise_type == 'flashcard' and 'questions' not in serializer.validated_data:
            questions, correct_answers = self._generate_flashcard_data(unlearned_words)
            serializer.save(
                questions=questions,
                correct_answers=correct_answers
            )
            return

        if exercise_type == 'multiple_choice' and not serializer.validated_data.get('questions'):
            words = wordset.words.all()
            questions, correct_answers = self._generate_m_choice_data(words)

            serializer.save(
                questions=questions,
                correct_answers=correct_answers
            )
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
            
            The word they needed to use is '{infinitive}' (base form of the word).
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
        print(user_answers)
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





prompt_text = (
    "Look at the image, extract only Lithuanian words and give me their English translation. "
    "For each word, return: "
    "- the original word exactly as it appears, "
    "- its English translation, "
    "- and its basic form (lemma), without changing the part of speech. "
    "IMPORTANT: The field name 'infinitive' is just a label and DOES NOT mean the word must be a verb. "
    "For nouns, return the nominative singular form in the 'infinitive' field. "
    "For verbs, return the actual infinitive form. "
    "For adjectives, use the masculine nominative singular form, and for other parts of speech, use the dictionary base form. "
    "Do NOT convert nouns into verbs. For example, do NOT convert 'stalas' (a noun) into 'stalauti' (a verb). "
    "Preserve the original part of speech. "
    "Format the output as a JSON array of objects with the following fields: "
    "'word' (original form), 'translation' (English meaning), and 'infinitive' (basic form). "
    "Example: [{\"word\": \"stalo\", \"translation\": \"table\", \"infinitive\": \"stalas\"}, "
    "{\"word\": \"eina\", \"translation\": \"goes\", \"infinitive\": \"eiti\"}]"
)



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


class TextExerciseAPIView(APIView):
    http_method_names = ['get']
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='wordset_id',
                description='ID of the wordset to use for the exercise',
                required=True,
                type=int
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Returns generated Lithuanian text and multiple choice questions",
                examples=[
                    {
                        "text": "Lithuanian text generated based on vocabulary...",
                        "questions": [
                            {
                                "question": "What does 'word' mean?",
                                "choices": ["option 1", "option 2", "option 3", "option 4"],
                                "correct_answer": "option 2"
                            }
                        ]
                    }
                ]
            ),
            400: OpenApiResponse(description="Wordset not found or insufficient words")
        },
        description="Generate Lithuanian text and multiple choice questions based on wordset vocabulary"
    )
    def get(self, request):
        wordset_id = request.query_params.get('wordset_id')
        if not wordset_id:
            return Response({"error": "wordset_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            wordset = WordSet.objects.get(id=wordset_id)
            if not wordset.words.exists():
                return Response({"error": "Wordset has no words"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get all words from the wordset
            words = list(wordset.words.all().values('word', 'translation', 'infinitive'))
            
            # Create the prompt for Gemini API
            prompt = self._create_text_prompt(words)
            
            # Generate text and questions using Gemini API
            generated_content = self._generate_text_and_questions(prompt)
            
            return Response(generated_content, status=status.HTTP_200_OK)
            
        except WordSet.DoesNotExist:
            return Response({"error": "Wordset not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _create_text_prompt(self, words):
        word_list = [f"{word['word']} ({word['translation']})" for word in words]
        word_list_formatted = ", ".join(word_list)
        
        prompt = f"""
        You are a Lithuanian language teacher helping beginners learn Lithuanian.
        
        Using the vocabulary list below, create:
        1. A coherent text in Lithuanian using as many words from the list as possible
        2. 5 multiple choice questions in simple Lituanian about the text to check comprehension
        
        Vocabulary list: {word_list_formatted}
        
        The text should:
        - Use beginner-friendly grammar and sentence structure
        - Include at least 50% of the words from the vocabulary list
        - Be contextual and meaningful (not just random sentences)
        
        The questions should:
        - Be in Lithuanian to test understanding
        - Each have 4 answer options (A, B, C, D)
        - Have varying difficulty levels
        
        Format your response as JSON with the following structure:
        {{
            "text": "Lithuanian text here...",
            "questions": [
                {{
                    "question": "Question 1",
                    "choices": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option B"
                }},
                ...more questions...
            ]
        }}
        """
        return prompt
    
    def _generate_text_and_questions(self, prompt):
        try:
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON content
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            content = json.loads(response_text)
            
            # Validate the expected structure
            if 'text' not in content or 'questions' not in content:
                raise ValueError("Response missing required fields")
                
            if not isinstance(content['questions'], list) or len(content['questions']) == 0:
                raise ValueError("Questions must be a non-empty list")
                
            for q in content['questions']:
                if not all(k in q for k in ('question', 'choices', 'correct_answer')):
                    raise ValueError("Question missing required fields")
                
            return content
            
        except Exception as e:
            print(f"Error generating content: {e}")
            raise ValueError(f"Failed to generate content: {str(e)}")



