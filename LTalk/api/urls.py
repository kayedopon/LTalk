from django.urls import path, include
from .views import WordViewSet, WordSetViewSet

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'word', WordViewSet, basename='words')
router.register(r'wordset', WordSetViewSet, basename='wordsets')

urlpatterns = [
    path('', include(router.urls)),
]
