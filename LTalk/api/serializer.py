from rest_framework import serializers
from main.models import Word, WordSet, Perfomance, WordProgress


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

    # override create function to addown implementation
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user 

        words = validated_data.pop('words')
        wordset = self.Meta.model.objects.create(**validated_data)

        for word in words:
            w, _ = Word.objects.get_or_create(word=word['word'], defaults=word)
            wordset.words.add(w)

        return wordset


class PerfomanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfomance
        fields = "__all__"
        read_only_fields = ['id']


class WordProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfomance
        fields = "__all__"
        read_only_fields = ['id', 'user', 'word']
        unique_together = ('user', 'word')

    def validate(self, data):
        if not ('correct_attempts' in data or 'incorrect_attempts' in data):
            raise serializers.ValidationError(
                "Either 'correct_attempts' or 'incorrect_attempts' must be provided."
            )
        return data

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
    
    
