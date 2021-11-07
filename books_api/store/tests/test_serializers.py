from django.test import TestCase
from store.models import Book
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        book_1 = Book.objects.create(name='Rework', price=75.00)
        book_2 = Book.objects.create(name='Everything is figureoutable', price=80.00)
        data = BooksSerializer([book_1, book_2], many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'Rework',
                'price': '75.00',
            },
            {
                'id': book_2.id,
                'name': 'Everything is figureoutable',
                'price': '80.00',
            },
        ]
        self.assertEqual(expected_data, data)