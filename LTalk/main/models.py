from django.db import models
from datetime import datetime
from authentication.models import User

class WordSet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wordsets')
    title = models.CharField(max_length=35, blank=False, null=False)
    description = models.CharField(max_length=200, blank=False, null=False)
    public = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Word(models.Model):
    word = models.CharField(max_length=35, null=False, blank=False)
    infinitive = models.CharField(max_length=35, null=False, blank=False)
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
        return str(self.score)
    

class WordProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    correct_attempts = models.IntegerField(default=0)
    incorrect_attempts = models.IntegerField(default=0)
    is_learned = models.BooleanField(default=False)


class Exercise(models.Model):
    EXERCISE_TYPES = [
        ('flashcard', 'Flash Card'),
        ('fill_blank', 'Fill in the blank'),
        ('multiple_choice', 'Multiple Choice'),
    ]
    wordset = models.ForeignKey(WordSet, on_delete=models.CASCADE, related_name='exercises')
    type = models.CharField(max_length=20, choices=EXERCISE_TYPES)
    question = models.TextField()
    correct_answer = models.TextField()

    def __str__(self):
        return f"{self.get_type_display()} for {self.wordset.title}"


