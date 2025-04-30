from django.urls import path
from .views import home, create_set, photo_processing

urlpatterns = [
    path('', home, name='home'),
    path('create-set', create_set, name='create_set'),
    path('photo-processing', photo_processing, name='photo-processing')
]
