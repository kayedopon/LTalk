from django.contrib import admin
from .models import WordSet, Word, Perfomance, WordProgress, Exercise


@admin.register(WordSet)
class WordSetAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'public', 'created',)
    search_fields = ('title', 'user__username')
    list_filter = ('public', 'created')


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('word', 'translation', )
    search_fields = ('word', 'translation')
    filter_horizontal = ('wordsets',)


@admin.register(Perfomance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('wordset', 'score', 'evaluation_date')
    list_filter = ('evaluation_date',)
    search_fields = ('wordset__title',)


@admin.register(WordProgress)
class WordProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'word', 'correct_attempts', 'incorrect_attempts', 'is_learned')
    list_filter = ('is_learned',)
    search_fields = ('user__username', 'word__word')


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('wordset', 'type', 'question')
    list_filter = ('type',)
    search_fields = ('wordset__title', 'question')
