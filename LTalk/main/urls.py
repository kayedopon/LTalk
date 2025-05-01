from django.urls import path
from .views import home, create_set, flashcard_practice

urlpatterns = [
    path('', home, name='home'),
    path('create-set', create_set, name='create_set'),
    path('wordset/<int:wordset_id>/flashcard/', flashcard_practice, name='flashcard_practice'),
]
