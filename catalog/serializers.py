from rest_framework import serializers
from .models import Book, Transaction

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "author", "isbn", "published_date", "copies_available"]
        read_only_fields = ["id"]

class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    book = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Transaction
        fields = ["id", "user", "book", "checkout_date", "return_date", "is_active"]
        read_only_fields = ["id", "user", "book", "checkout_date", "return_date", "is_active"]

