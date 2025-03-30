from rest_framework import serializers
from ...models import Post, Category
# class PostSerializer(serializers.Serializer):
    
#     title = serializers.CharField(max_length=255)
#     id = serializers.IntegerField()

class PostSerializer(serializers.ModelSerializer):
    # content = serializers.CharField(read_only=True)
    # content = serializers.ReadOnlyField()
    class Meta:
        model = Post
        fields = ['id', 'author','title', 'content', 'status', 'created_date', 'published_date']
        # read_only_fields = ['content']


class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ['id', 'name']