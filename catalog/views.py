from django.db import transaction as db_tx
from django.db.models import Q
from django.utils import timezone

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Book, Transaction
from .serializers import BookSerializer, TransactionSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

class BookViewSet(viewsets.ModelViewSet):
    """
    Books CRUD + filtering.
    Filters:
      - ?available=true|false
      - ?title=...
      - ?author=...
      - ?isbn=...
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()

        available = self.request.query_params.get("available")
        title = self.request.query_params.get("title")
        author = self.request.query_params.get("author")
        isbn = self.request.query_params.get("isbn")

        if available is not None:
            if available.lower() in ("true", "1", "yes"):
                qs = qs.filter(copies_available__gt=0)
            elif available.lower() in ("false", "0", "no"):
                qs = qs.filter(copies_available__lte=0)

        if title:
            qs = qs.filter(title__icontains=title)
        if author:
            qs = qs.filter(author__icontains=author)
        if isbn:
            qs = qs.filter(isbn__icontains=isbn)

        return qs.order_by("title", "author")

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only listing of transactions.
    Use custom actions for checkout & return.
    """
    queryset = Transaction.objects.select_related("user", "book")
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="checkout")
    def checkout(self, request):
        """
        Checkout an available book for the current user.
        Payload: { "book_id": <int> }
        Rules:
          - Decrement copies if available.
          - Disallow multiple active checkouts of same book per user.
        """
        user = request.user
        book_id = request.data.get("book_id")

        if not book_id:
            return Response({"detail": "book_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        with db_tx.atomic():
            # Lock the book row to prevent race conditions.
            try:
                book = Book.objects.select_for_update().get(pk=book_id)
            except Book.DoesNotExist:
                return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

            if book.copies_available <= 0:
                return Response({"detail": "No copies available."}, status=status.HTTP_409_CONFLICT)

            # Check if user already holds an active checkout for this book.
            already_active = Transaction.objects.select_for_update().filter(
                user=user, book=book, return_date__isnull=True
            ).exists()
            if already_active:
                return Response(
                    {"detail": "You already have an active checkout for this book."},
                    status=status.HTTP_409_CONFLICT,
                )

            # Create the transaction & decrement copies
            tx = Transaction.objects.create(user=user, book=book)
            book.copies_available -= 1
            book.save(update_fields=["copies_available"])

        return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="return")
    def return_book(self, request):
        """
        Return a currently checked-out book.
        Payload: { "book_id": <int> }
        Rules:
          - Set return_date.
          - Increment copies_available.
        """
        user = request.user
        book_id = request.data.get("book_id")

        if not book_id:
            return Response({"detail": "book_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        with db_tx.atomic():
            # Find active transaction and lock it.
            tx = (
                Transaction.objects.select_for_update()
                .filter(user=user, book_id=book_id, return_date__isnull=True)
                .first()
            )
            if not tx:
                return Response({"detail": "No active checkout found for this book."}, status=status.HTTP_400_BAD_REQUEST)

            tx.return_date = timezone.now()
            tx.save(update_fields=["return_date"])

            book = Book.objects.select_for_update().get(pk=book_id)
            book.copies_available += 1
            book.save(update_fields=["copies_available"])

        return Response(TransactionSerializer(tx).data, status=status.HTTP_200_OK)

