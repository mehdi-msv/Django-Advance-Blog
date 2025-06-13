from rest_framework import permissions


class IsAuthenticatedForRetrieve(permissions.IsAuthenticatedOrReadOnly):
    def has_permission(self, request, view):
        if view.action == "retrieve":
            return request.user and request.user.is_authenticated
        return True


class HasAddPostPermission(permissions.BasePermission):
    """
    Allows access only to users with the 'blog.add_post' permission.
    """
    def has_permission(self, request, view):
        return request.user.has_perm("blog.add_post")