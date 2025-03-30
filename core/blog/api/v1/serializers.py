from rest_framework import serializers
from ...models import Post, Category
# class PostSerializer(serializers.Serializer):
    
#     title = serializers.CharField(max_length=255)
#     id = serializers.IntegerField()

class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ['id', 'name']
        
        
class PostSerializer(serializers.ModelSerializer):
    # content = serializers.CharField(read_only=True)
    # content = serializers.ReadOnlyField()
    snippet = serializers.ReadOnlyField(source='get_snippet')
    relative_url = serializers.URLField(source='get_absolute_api_url', read_only=True)
    absolute_url = serializers.SerializerMethodField()
    category = CategorySerializer()
    class Meta:
        model = Post
        fields = ['id', 'author','title', 'content', 'status', 'relative_url' , 'absolute_url' , 'snippet' ,'created_date', 'published_date']
        # read_only_fields = ['content']

    def get_absolute_url(self,obj):
        request = self.context.get('request')
        absolute_url = obj.get_absolute_api_url()
        return request.build_absolute_uri(absolute_url)
    def to_representation(self, instance):
        
        return super().to_representation(instance)
        
