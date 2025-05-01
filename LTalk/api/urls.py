from django.urls import path, include
from .views import WordViewSet, WordSetViewSet, SubmitExerciseAPIView, WordProgressViewSet, ExerciseViewSet

from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


router = routers.DefaultRouter()
router.register(r'word', WordViewSet, basename='word')
router.register(r'wordset', WordSetViewSet, basename='wordset')
router.register(r'wordprogress', WordProgressViewSet, basename='word-progress')
router.register(r'exercise', ExerciseViewSet, basename='excercise')

urlpatterns = [
    path('', include(router.urls)),
    path('exercise/<int:exercise_id>/submit/', SubmitExerciseAPIView.as_view(), name='submit-exercise'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]
