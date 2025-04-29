from django.urls import path, include
from .views import WordViewSet, WordSetViewSet

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'word', WordViewSet, basename='word')
router.register(r'wordset', WordSetViewSet, basename='wordset')
router.register(r'perfomance', WordSetViewSet, basename='perfomance')
router.register(r'wordprogress', WordSetViewSet, basename='wordprogress')

urlpatterns = [
    path('', include(router.urls)),
]
