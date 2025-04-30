from django.contrib import admin
from .models import WordSet, Word, WordProgress, Exercise


@admin.register(WordSet)
class WordSetAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'public', 'created',)
    search_fields = ('title', 'user__username')
    list_filter = ('public', 'created')


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('word', 'infinitive', 'translation', )
    search_fields = ('word', 'infinitive', 'translation')
    filter_horizontal = ('wordsets',)


@admin.register(WordProgress)
class WordProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'word', 'correct_attempts', 'incorrect_attempts', 'is_learned')
    list_filter = ('is_learned',)
    search_fields = ('user__username', 'word__word')


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('wordset', 'type', )
    list_filter = ('type',)
    search_fields = ('wordset__title',)
