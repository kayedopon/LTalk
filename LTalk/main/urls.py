from django.urls import path
from .views import home, create_set, wordset_detail

urlpatterns = [
    path('', home, name='home'),
    path('create-set', create_set, name='create_set'),
    path('wordsets/<int:id>/', wordset_detail, name='wordset_detail'),
]
