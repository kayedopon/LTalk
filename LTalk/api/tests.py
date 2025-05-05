from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from authentication.models import User
from django.urls import reverse
from rest_framework import status
from main.models import Exercise, WordProgress, WordSet, Word

class WordSetAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass', email="otheruser@gmail.com")
        self.client = APIClient()
        self.client.login(email="otheruser@gmail.com", password='testpass')

        self.word_data = {
            "word": "labas",
            "infinitive": "labinti",
            "translation": "hello"
        }

        self.wordset_data = {
            "title": "My Word Set",
            "description": "Test description",
            "public": True,
            "words": [self.word_data]
        }

    def test_create_wordset(self):
        response = self.client.post("/api/wordset/", self.wordset_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WordSet.objects.count(), 1)

    def test_list_own_wordsets(self):
        self.client.post("/api/wordset/", self.wordset_data, format='json')
        response = self.client.get("/api/wordset/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_list_others_wordsets(self):
        other_user = User.objects.create_user(username='otheruser', password='otherpass', email="otheruser2@gmail.com")
        wordset = WordSet.objects.create(user=other_user, title="Other's Set", public=True)
        word = Word.objects.create(**self.word_data)
        wordset.words.add(word)

        response = self.client.get("/api/wordset/?scope=others")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(ws['title'] == "Other's Set" for ws in response.data['results']))

    def test_duplicate_wordset(self):
        other_user = User.objects.create_user(username='otheruser', password='otherpass', email="otheruser2@gmail.com")
        original = WordSet.objects.create(user=other_user, title="Public Set", public=True)
        word = Word.objects.create(**self.word_data)
        original.words.add(word)

        url = f"/api/wordset/{original.id}/duplicate/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WordSet.objects.filter(user=self.user).count(), 1)

    def test_delete_wordset(self):
        # Create a word set
        create_url = reverse('wordset-list')
        create_data = {
            "title": "To Delete",
            "description": "Will be deleted",
            "public": False,
            "words": [
                {"word": "delete", "infinitive": "delete", "translation": "ištrinti"}
            ]
        }

        response = self.client.post(create_url, create_data, format='json')

        # Check creation succeeded
        self.assertEqual(response.status_code, 201, msg=f"Create failed: {response.data}")
        self.assertIn('id', response.data)

        wordset_id = response.data['id']

        # Delete the word set
        delete_url = reverse('wordset-detail', args=[wordset_id])
        delete_response = self.client.delete(delete_url)

        self.assertEqual(delete_response.status_code, 204)

class WordAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass', email="testuser@gmail.com")
        self.client = APIClient()
        self.client.login(email="testuser@gmail.com", password='testpass')
        self.word = Word.objects.create(word="ačiū", infinitive="ačiūti", translation="thank you")

    def test_list_words(self):
        response = self.client.get("/api/word/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(w['word'] == "ačiū" for w in response.data['results']))


class ExerciseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="user1", password="pass", email="user1@gmail.com")
        self.user2 = User.objects.create_user(username="user2", password="pass", email="user2@gmail.com")

        self.wordset = WordSet.objects.create(title="Test Set", user=self.user1)
        self.word1 = Word.objects.create(word="cat", infinitive="test", translation="katė")
        self.word2 = Word.objects.create(word="dog", infinitive="test", translation="šuo")
        self.wordset.words.add(self.word1)
        self.wordset.words.add(self.word2)

        WordProgress.objects.create(user=self.user1, word=self.word1)
        WordProgress.objects.create(user=self.user2, word=self.word2)

    def test_word_progress_filtered_by_user(self):
        self.client.force_authenticate(self.user1)
        response = self.client.get("/api/wordprogress/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]["word"], self.word1.id)

    def test_create_flashcard_exercise(self):
        self.client.force_authenticate(self.user1)
        response = self.client.post("/api/exercise/", {
            "type": "flashcard",
            "wordset": self.wordset.id
        }, format="json")
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("questions", data)
        self.assertIn("correct_answers", data)
        self.assertEqual(data["type"], "flashcard")
        self.assertTrue(Exercise.objects.filter(id=data["id"], wordset=self.wordset).exists())


class SubmitExerciseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="user", password="pass", email="user@gmail.com")
        self.client.login(email="user@gmail.com", password="pass")

        self.wordset = WordSet.objects.create(title="Test Set", user=self.user)
        self.word1 = Word.objects.create(word="cat", infinitive="test", translation="katė")
        self.word2 = Word.objects.create(word="dog", infinitive="test", translation="šuo")
        self.wordset.words.add(self.word1)
        self.wordset.words.add(self.word2)

        response1 = self.client.post("/api/exercise/", {
            "type": "flashcard",
            "wordset": self.wordset.id
        }, format="json")

        response2 = self.client.post("/api/exercise/", {
            "type": "multiple_choice",
            "wordset": self.wordset.id
        }, format="json")

        self.data1 = response1.json()
        self.data2 = response2.json()

    def test_submit_exercise(self):
        response1 = self.client.post(f"/api/exercise/{self.data1["id"]}/submit/", {
            "user_answers": self.data1['correct_answers']
        }, format='json')
        response2 = self.client.post(f"/api/exercise/{self.data2["id"]}/submit/", {
            "user_answers": self.data2['correct_answers']
        }, format='json')

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)



class ProcessPhotoAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="user", password="pass", email="user@gmail.com")
        self.client.login(email="user@gmail.com", password="pass")

        self.image_path = "api/images/food.png"
        self.url = reverse('process_photo')

    def test_process_photo(self):
        img = Image.open(self.image_path)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        uploaded_file = SimpleUploadedFile("food.png", buffer.read(), content_type="image/png")

        response = self.client.post(self.url, {'image': uploaded_file}, format='multipart')
        self.assertEqual(response.status_code, 200)