import json
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self) -> None:  # this method will run every time new test would be executed
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(name='Rework', price=75.00, author="Author 1", owner=self.user)
        self.book_2 = Book.objects.create(name='Everything is figureoutable', price=80.00, author="Maria")
        self.book_3 = Book.objects.create(name='Never give up Maria', price=90.00, author="Author 3")

    def test_get_data(self):
        url = reverse('book-list')
        print(url)
        response = self.client.get(url)
        serializer_data = BooksSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        print(response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Maria'})
        serializer_data = BooksSerializer([self.book_2, self.book_3], many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_create(self):
        url = reverse('book-list')
        data = {
            'name': 'Programming in Python 3',
            'price': 150.00,
            'author': "Edward Snowden",
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test_username2')
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': 575,
            'author': "Edward Snowden",
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        print(response.data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.book_1.refresh_from_db()  # refreshing a particular model
        self.assertEqual(75, self.book_1.price)

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_username2', is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': 575,
            'author': "Edward Snowden",
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        print(response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()  # refreshing a particular model
        self.assertEqual(575, self.book_1.price)


class BooksRelationTestCase(APITestCase):
    def setUp(self) -> None:  # this method will run every time new test would be executed
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username2')
        self.book_1 = Book.objects.create(name='Rework', price=75.00, author="Author 1", owner=self.user)
        self.book_2 = Book.objects.create(name='Everything is figureoutable', price=80.00, author="Maria")

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'rate': 3,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')  # patch similar to get put length can be leverage
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual(3, relation.rate)

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'like': True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')  # patch similar to get put length can be leverage
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.like)
        data = {
            'in_bookmarks': True,
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')  # patch similar to get put length can be leverage
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.in_bookmarks)
