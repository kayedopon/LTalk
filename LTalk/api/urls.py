from django.urls import path, include
from .views import WordViewSet, WordSetViewSet, SubmitExerciseAPIView, WordProgressViewSet

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'word', WordViewSet, basename='word')
router.register(r'wordset', WordSetViewSet, basename='wordset')
router.register(r'wordprogress', WordProgressViewSet, basename='wordprogress')

urlpatterns = [
    path('', include(router.urls)),
    path('exercises/<int:exercise_id>/submit/', SubmitExerciseAPIView.as_view(), name='submit-exercise'),
]
