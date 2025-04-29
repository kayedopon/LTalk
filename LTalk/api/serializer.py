from rest_framework import serializers
from main.models import Word, WordSet


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
        print(validated_data)
        words = validated_data.pop('words')
        wordset = self.Meta.model.objects.create(**validated_data)

        for word in words:
            w, _ = Word.objects.get_or_create(word=word['word'], defaults=word)
            wordset.words.add(w)

        return wordset

    