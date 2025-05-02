from django.db import models
from datetime import datetime
from authentication.models import User

class WordSet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wordsets')
    title = models.CharField(max_length=35, blank=False, null=False)
    description = models.CharField(max_length=200, blank=True, null=True)
    public = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def learned_percent(self, user):
        words = self.words.all()
        total = words.count()
        if total == 0:
            return 0
        learned = words.filter(wordprogress__user=user, wordprogress__is_learned=True).count()
        return int((learned / total) * 100)

    def __str__(self):
        return self.title

class Word(models.Model):
    word = models.CharField(max_length=35, null=False, blank=False)
    infinitive = models.CharField(max_length=35, null=False, blank=False)
    translation = models.CharField(max_length=35, null=False, blank=False)
    wordsets = models.ManyToManyField(WordSet, related_name="words")

    def __str__(self):
        return self.word
    

class WordProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    correct_attempts = models.IntegerField(default=0)
    incorrect_attempts = models.IntegerField(default=0)
    is_learned = models.BooleanField(default=False)


    def update_progress(self, correct: bool):
        if correct:
            self.correct_attempts += 1
        else:
            self.incorrect_attempts += 1

        total = self.correct_attempts + self.incorrect_attempts
        ratio = self.correct_attempts / total if total > 0 else 0
        self.is_learned = self.correct_attempts >= 3 and ratio >= 0.7
        self.save()


class Exercise(models.Model):
    EXERCISE_TYPES = [
        ('flashcard', 'Flash Card'),
        ('multiple_choice', 'Multiple Choice'),
        ('fill_in_gap', 'Fill in the Gap'),
    ]
    wordset = models.ForeignKey(WordSet, on_delete=models.CASCADE, related_name='exercises')
    type = models.CharField(max_length=20, choices=EXERCISE_TYPES)
    questions = models.JSONField()
    correct_answers = models.JSONField()

    def __str__(self):
        return f"{self.get_type_display()} for {self.wordset.title}"


class ExerciseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_progress')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='progress_entries')
    user_answer = models.JSONField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)
    grade = models.CharField()

    def __str__(self):
        return f"{self.user} - {self.exercise} - {'Correct' if self.is_correct else 'Incorrect'}"


