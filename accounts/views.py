from rest_framework import viewsets, permissions
from .models import User
from .serializers import UserSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admins can do everything.
    Non-admins: read-only (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

class UserViewSet(viewsets.ModelViewSet):
    """
    Users CRUD.
    - Admins can create/update/delete users.
    - Everyone can list/retrieve (tweak as needed).
    """
    queryset = User.objects.all().order_by("username")
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]

