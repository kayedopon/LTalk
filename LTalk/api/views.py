from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .serializer import WordSerializer, WordSetSerializer, PerfomanceSerializer, WordProgressSerializer
from main.models import Word, WordSet, Perfomance, WordProgress



class WordViewSet(ModelViewSet):
   
    serializer_class = WordSerializer
    queryset = Word.objects.all()
    http_method_names = ['get', 'head', 'options']


class WordSetViewSet(ModelViewSet):

    serializer_class = WordSetSerializer
    queryset = WordSet.objects.all()


class PerfomanceViewSet(ModelViewSet):

    serializer_class = PerfomanceSerializer
    queryset = Perfomance.objects.all()


class WordProgressViewSet(ModelViewSet):

    serializer_class = WordProgressSerializer
    queryset = WordProgress.objects.all()
    
