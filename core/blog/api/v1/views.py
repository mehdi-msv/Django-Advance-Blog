from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.core.cache import cache
from django.db.models import Q, F, Value, CharField
from django.utils import timezone
from django.db.models.functions import Concat

from .permissions import HasAddPostPermission, IsAuthenticatedForRetrieve
from .paginations import PostsPagination
from .serializers import PostSerializer, CategorySerializer
from ...models import Post, Category, CommentReport, Comment
from ...tasks import create_comment_task


class PostModelViewSet(ModelViewSet):
    """
    API endpoint for Posts management.

    Features:
    - Cached pagination for list view.
    - Filter by category name and author email.
    - Search by author's full name, title, and content.
    - Ordering by publish date, creation date, and author full name.
    - Only authors can update/delete their own posts.
    """

    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedForRetrieve]
    pagination_class = PostsPagination
    lookup_field = "slug"

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category__name"]
    search_fields = ["author_full_name", "title", "content"]
    ordering_fields = ["published_date"]
    ordering = ["-published_date"]

    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.annotate(
            author_full_name=Concat(
                F("author__first_name"),
                Value(" "),
                F("author__last_name"),
                output_field=CharField(),
            )
        )

        if self.action == "list":
            page = self.request.query_params.get("page", 1)
            cache_key = f"post_list_page_{page}"
            cached = cache.get(cache_key)
            if cached:
                return cached

            filtered = queryset.filter(
                status=True, published_date__lte=timezone.now()
            )
            cache.set(
                cache_key, filtered, timeout=600
            )  # Cache for 10 minutes
            return filtered

        if self.action == "retrieve":
            return queryset.filter(
                (
                    Q(status=True, published_date__lte=timezone.now())
                    | Q(author__user=user)
                )
            )

        # Restrict update/delete to user's own posts
        return queryset.filter(author__user=user)

    def get_permissions(self):
        if self.action == "create":
            return [HasAddPostPermission()]
        return super().get_permissions()

    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated]
    )
    def comment(self, request, slug=None):
        """
        Submit a comment asynchronously via Celery.
        Supports nested replies with optional 'parent' field.
        """
        text = request.data.get("text")
        parent_id = request.data.get("parent")

        create_comment_task.delay(
            post_slug=slug,
            profile_id=request.user.profile.id,
            text=text,
            parent_id=parent_id,
        )
        return Response(
            {"detail": "Comment submitted and pending approval."},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(
        detail=False, methods=["post"], permission_classes=[IsAuthenticated]
    )
    def report_comment(self, request):
        """
        Report a comment by ID.
        - User cannot report own comment.
        - Duplicate reports ignored.
        """
        comment_id = request.data.get("comment_id")
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {"detail": "Comment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if comment.author == request.user.profile:
            return Response(
                {"detail": "You cannot report your own comment."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if CommentReport.objects.filter(
            user=request.user.profile, comment=comment
        ).exists():
            return Response(
                {"detail": "You have already reported this comment."},
                status=status.HTTP_200_OK,
            )

        CommentReport.objects.create(
            user=request.user.profile, comment=comment
        )
        comment.report()  # Increase report count or trigger logic
        return Response(
            {"detail": "Report submitted."}, status=status.HTTP_201_CREATED
        )


class CategoryModelViewSet(ModelViewSet):
    """
    API endpoint for managing categories.
    Supports list, create, retrieve, update, and delete operations.
    Access restricted to admin users.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    lookup_field = "name"  # Use 'name' instead of default 'pk' for lookups
