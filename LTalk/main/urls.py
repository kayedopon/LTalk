from django.urls import path
from .views import home, create_set

urlpatterns = [
    path('', home, name='home'),
    path('create-set', create_set, name='create_set'),
]
