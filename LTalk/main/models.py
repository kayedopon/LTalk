from django.db import models
from datetime import datetime

class WordSet(models.Model):
    ##user =
    title = models.CharField(max_length=35, blank=False, null=False)
    description = models.CharField(max_length=200, blank=False, null=False)
    public = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=datetime.now())

    def __str__(self):
        return self.title

class Word(models.Model):
    word = models.CharField(max_length=35, null=False, blank=False)
    translation = models.CharField(max_length=35, null=False, blank=False)
    wordsets = models.ManyToManyField(WordSet, related_name="words")

    def __str__(self):
        return self.word
    
class Perfomance(models.Model):
    wordset = models.ForeignKey(WordSet, on_delete=models.CASCADE, related_name='performances')
    score = models.IntegerField(blank=False, null=False)
    evaluation_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.score


