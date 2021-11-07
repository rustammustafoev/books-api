from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from store.models import Book
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):
    def test_get(self):
        book_1 = Book.objects.create(name='Rework', price=75.00)
        book_2 = Book.objects.create(name='Everything is figureoutable', price=80.00)
        url = reverse('book-list')
        print(url)
        response = self.client.get(url)
        serializer_data = BooksSerializer([book_1, book_2], many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        print(response.data)
