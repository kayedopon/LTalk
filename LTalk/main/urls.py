from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create-set', views.create_set, name='create_set'),
    path('wordset/<int:wordset_id>/flashcard/', views.flashcard_practice, name='flashcard_practice'),
    path('wordset/<int:wordset_id>/fill-in-gap/', views.fill_in_gap_practice, name='fill_in_gap_practice'),
    path('wordset/<int:id>/multiple-choice', views.m_choice_practice, name='m_choice_practice'),
    path('wordset/<int:id>/', views.wordset_detail, name='wordset_detail'),
    path('wordset/<int:id>/history', views.exercise_history, name='exercise_history'),
    path('explore', views.explore_sets, name="explore_sets")
    
]
