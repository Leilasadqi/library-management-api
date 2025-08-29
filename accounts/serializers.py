from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Exposes the required fields for Users CRUD.
    Note: password handling is kept simple here. For production, you'd use write-only
    passwords and create_user to hash them.
    """
    class Meta:
        model = User
        fields = ["id", "username", "email", "date_of_membership", "is_active"]
        read_only_fields = ["id", "date_of_membership"]

