from django.urls import path
from .views import home, photo_processing, wordset_list

urlpatterns = [
    path('', home, name='home'),
    path('photo-processing', photo_processing, name='photo-processing'),
    path('wordsets', wordset_list, name="wordset-list"),
]
