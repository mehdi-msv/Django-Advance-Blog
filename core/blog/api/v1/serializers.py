from rest_framework import serializers
from ...models import Post, Category
from accounts.models import Profile

# class PostSerializer(serializers.Serializer):

#     title = serializers.CharField(max_length=255)
#     id = serializers.IntegerField()


class CategorySerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "absolute_url"]

    def get_absolute_url(self, obj):
        request = self.context.get("request")
        absolute_url = obj.get_absolute_api_url()
        return request.build_absolute_uri(absolute_url)

    def to_representation(self, instance):
        request = self.context.get("request")
        rep = super().to_representation(instance)
        if request.parser_context.get("kwargs").get("pk"):
            rep.pop("absolute_url", None)
        if not request.user.is_staff:
            rep.pop("absolute_url", None)
            return rep
        return rep


class PostSerializer(serializers.ModelSerializer):
    # content = serializers.CharField(read_only=True)
    # content = serializers.ReadOnlyField()
    snippet = serializers.ReadOnlyField(source="get_snippet")
    relative_url = serializers.URLField(source="get_absolute_api_url", read_only=True)
    absolute_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "image",
            "title",
            "content",
            "status",
            "relative_url",
            "absolute_url",
            "category",
            "snippet",
            "created_date",
            "published_date",
        ]
        read_only_fields = ["author"]

    def get_absolute_url(self, obj):
        request = self.context.get("request")
        absolute_url = obj.get_absolute_api_url()
        return request.build_absolute_uri(absolute_url)

    def to_representation(self, instance):

        request = self.context.get("request")
        rep = super().to_representation(instance)
        rep["category"] = CategorySerializer(
            instance.category, context={"request": request}
        ).data  # if use nested serializer the request must be sent in context

        if request.parser_context.get("kwargs").get("pk"):
            rep.pop("snippet", None)
            rep.pop("absolute_url", None)
            rep.pop("relative_url", None)

        else:
            rep.pop("content")

        if not rep["category"]["name"]:
            rep["category"]["name"] = "Uncategorized"
        return rep

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["author"] = Profile.objects.get(user__id=request.user.id)
        return super().create(validated_data)
