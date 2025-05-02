from rest_framework import serializers
from main.models import ExerciseProgress, Word, WordSet, WordProgress, Exercise


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ['id', 'word', 'infinitive', 'translation']
        read_only_fields = ['id']


class WordSetSerializer(serializers.ModelSerializer):
    words = WordSerializer(many=True)
    class Meta:
        model = WordSet
        fields = ['id', 'user', 'title', 'description', 'public', 'created', 'words']
        read_only_fields = ['id', 'user', 'created']

    # override create function to add own implementation
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user 

        words = validated_data.pop('words')
        wordset = self.Meta.model.objects.create(**validated_data)

        for word in words:
            w, _ = Word.objects.get_or_create(word=word['word'], defaults=word)
            wordset.words.add(w)

        return wordset


class WordProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordProgress
        fields = "__all__"
        read_only_fields = ['id', 'user', 'word']
        unique_together = ('user', 'word')

    # override validate function
    def validate(self, data):
        if not ('correct_attempts' in data or 'incorrect_attempts' in data):
            raise serializers.ValidationError(
                "Either 'correct_attempts' or 'incorrect_attempts' must be provided."
            )
        return data

    # override update function
    def update(self, instance, validated_data):
        correct = validated_data.get('correct_attempts')
        incorrect = validated_data.get('incorrect_attempts')

        if correct == 1:
            instance.correct_attempts += 1
        elif incorrect == 1:
            instance.incorrect_attempts += 1

        instance.is_learned = instance.correct_attempts > instance.incorrect_attempts
        instance.save()
        return instance
    

class ExerciseSerializer(serializers.ModelSerializer):
    questions = serializers.JSONField(required=False)
    correct_answers = serializers.JSONField(required=False)

    class Meta:
        model = Exercise
        fields = ['id', 'wordset', 'type', 'questions', 'correct_answers']
        read_only_fields = ['id']
        # unique_together = ('wordset', 'type')


    def validate(self, data):
        exercise_type = data.get('type')
        questions = data.get('questions')
        correct_answers = data.get('correct_answers')
        wordset = data.get('wordset')
        is_creating = self.instance is None

        # If creating a flashcard exercise and questions/answers are missing, it's okay (view handles it)
        if self.instance is None and exercise_type in ['flashcard', 'multiple_choice'] and not questions and not correct_answers:
            if not wordset or not wordset.words.exists():
                raise serializers.ValidationError("Cannot create exercise for an empty wordset.")
            return data  # allow view to auto-generate

        # Ensure questions/answers are dicts if provided
        if questions is not None and not isinstance(questions, dict):
             raise serializers.ValidationError({'questions': "Must be a dictionary if provided."})
        if correct_answers is not None and not isinstance(correct_answers, dict):
             raise serializers.ValidationError({'correct_answers': "Must be a dictionary if provided."})

        # If questions/answers are provided (e.g., for non-flashcard types or explicit creation)
        if questions is not None or correct_answers is not None:
            if not questions: # Check if one is provided but not the other
                 raise serializers.ValidationError({'questions': "Cannot be empty if correct_answers is provided."})
            if not correct_answers:
                 raise serializers.ValidationError({'correct_answers': "Cannot be empty if questions is provided."})

            if set(questions.keys()) != set(correct_answers.keys()):
                raise serializers.ValidationError("Keys of 'questions' and 'correct_answers' must match when provided.")

        return data
    

class ExerciseProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseProgress
        fields = ['id', 'user', 'exercise', 'user_answer', 'is_correct', 'answered_at', 'grade']
        read_only_fields = ['id', 'answered_at']

    def validate_user_answer(self, value):
        if not value:
            raise serializers.ValidationError("User answer cannot be empty.")
        return value
    
    def validate(self, data):
        if 'is_correct' not in data:
            raise serializers.ValidationError("The field 'is_correct' must be provided.")
        return data
