from django.conf import settings
from django.db import models
from django.utils import timezone

class Book(models.Model):
    """
    Represents a library book.
    """
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True, db_index=True)
    published_date = models.DateField(null=True, blank=True)
    copies_available = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["title", "author"]

    def __str__(self) -> str:
        return f"{self.title} — {self.author} ({self.isbn})"


class Transaction(models.Model):
    """
    A checkout/return record.
    - return_date = null means the book is currently checked out.
    - UniqueConstraint(active): prevent same user from holding multiple active copies
      of the same book (enforces 'one copy per user' rule).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="transactions")
    checkout_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"],
                condition=models.Q(return_date__isnull=True),
                name="unique_active_checkout_per_user_book",
            )
        ]
        ordering = ["-checkout_date"]

    def mark_returned(self) -> None:
        """Helper to set the return date."""
        if not self.return_date:
            self.return_date = timezone.now()
            self.save(update_fields=["return_date"])

    @property
    def is_active(self) -> bool:
        return self.return_date is None

    def __str__(self) -> str:
        state = "OUT" if self.is_active else "RETURNED"
        return f"{self.user} -> {self.book} [{state}]"

