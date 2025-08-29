from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    date_of_membership = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.username

