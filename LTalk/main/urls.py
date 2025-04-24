from django.urls import path
from .views import home, photo_processing

urlpatterns = [
    path('', home, name='home'),
    path('photo-processing', photo_processing, name='photo-processing')
]
