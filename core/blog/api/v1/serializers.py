from rest_framework import serializers

from ...models import Post, Category, Comment
from accounts.models import Profile


class CategorySerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "absolute_url"]

    def get_absolute_url(self, obj):
        """
        Return full absolute URL for the category's API endpoint.
        """
        request = self.context.get("request")
        absolute_url = obj.get_absolute_url()
        return request.build_absolute_uri(absolute_url)

    def to_representation(self, instance):
        """
        Customize representation based on request context:
        - Remove 'absolute_url' if lookup by 'pk' is used.
        - Hide 'absolute_url' for non-staff users.
        """
        request = self.context.get("request")
        rep = super().to_representation(instance)

        # If detail view accessed via 'pk', remove absolute_url
        if request.parser_context.get("kwargs", {}).get("pk"):
            rep.pop("absolute_url", None)

        # Only staff users can see absolute_url field
        if not request.user.is_staff:
            rep.pop("absolute_url", None)

        return rep


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "author", "text", "created_at"]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.full_name", read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "author", "text", "created_at", "replies"]

    def get_replies(self, obj):
        replies = obj.replies.filter(is_approved=True, is_hidden=False)
        return CommentSerializer(replies, many=True).data


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for Post model.

    - Shows author as full name or email.
    - Shows category name instead of ID.
    - Allows write-only category_id for create/update.
    - Hides content and comments in list view.
    - Adds relative and absolute URLs.
    """

    category = serializers.SerializerMethodField(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True, source="category"
    )
    author = serializers.CharField(source="author.full_name", read_only=True)
    snippet = serializers.ReadOnlyField(source="get_snippet")
    absolute_url = serializers.SerializerMethodField(read_only=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "title",
            "image",
            "snippet",
            "content",
            "author",
            "category",
            "category_id",
            "status",
            "published_date",
            "absolute_url",
            "comments",
        ]
        read_only_fields = ["author"]

    def get_category(self, obj):
        return obj.category.name if obj.category else None

    def get_absolute_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.get_absolute_url())

    def get_comments(self, obj):
        request = self.context.get("request")
        if request and request.parser_context.get("kwargs", {}).get("slug"):
            qs = Comment.objects.filter(
                post=obj,
                parent__isnull=True,
                is_hidden=False,
                is_approved=True,
            ).prefetch_related("replies")
            return CommentSerializer(qs, many=True).data
        return None

    def to_representation(self, instance):
        request = self.context.get("request")
        rep = super().to_representation(instance)
        if not request.parser_context.get("kwargs", {}).get("slug"):
            rep.pop("comments")
            rep.pop("content")
        else:
            rep.pop("snippet")
        return rep

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["author"] = Profile.objects.get(user=request.user)
        if "image" not in validated_data or validated_data["image"] in [
            None,
            "",
        ]:
            validated_data["image"] = "defaults/default_post.png"
        return super().create(validated_data)

    def update(self, instance, validated_data):
        image = validated_data.get("image", serializers.empty)
        if image in [None, ""]:
            validated_data["image"] = instance.image
        return super().update(instance, validated_data)
