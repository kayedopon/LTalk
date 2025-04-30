from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from .serializer import ExerciseProgressSerializer, WordSerializer, WordSetSerializer, WordProgressSerializer
from main.models import Word, WordSet, WordProgress, Exercise, ExerciseProgress


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
    

class SubmitExerciseAPIView(APIView):
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

            for word in related_words:
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


