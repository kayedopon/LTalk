from django.urls import path
from .views import home, create_set, flashcard_practice, wordset_detail, exercise_history

urlpatterns = [
    path('', home, name='home'),
    path('create-set', create_set, name='create_set'),
    path('wordset/<int:wordset_id>/flashcard/', flashcard_practice, name='flashcard_practice'),
    path('wordset/<int:id>/', wordset_detail, name='wordset_detail'),
    path('wordset/<int:id>/history', exercise_history, name='exercise_history')
]
