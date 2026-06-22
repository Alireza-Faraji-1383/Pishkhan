from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow safe methods for all; write methods only for object owner."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsOwner(permissions.BasePermission):
    """Allow access only if the requesting user owns the object."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
