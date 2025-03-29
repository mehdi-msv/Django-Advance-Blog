
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .serializers import PostSerializer , CategorySerializer
from ...models import Post , Category
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

"""
# from rest_framework.decorators import api_view,permission_classes

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def postList(request):
    if request.method == "GET":
        posts = Post.objects.filter(status=True)
        serializer = PostSerializer(posts,many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        @api_view(["GET", "PUT", "DELETE"])
        
        
@permission_classes([IsAuthenticatedOrReadOnly])
def postDetail(request,id):
    # try:
    #     post = Post.objects.get(pk=id)
    #     serializer = PostSerializer(post)
    #     return Response(serializer.data)
    # except Post.DoesNotExist:
    #     return Response('{detail:not found}', status=status.HTTP_404_NOT_FOUND)
    post = get_object_or_404(Post,pk=id,status=True)
    if request.method == "GET":
        serializer = PostSerializer(post)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = PostSerializer(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == "DELETE":
        post.delete()
        return Response({"detail": "Your post has been successfully removed."},status=status.HTTP_204_NO_CONTENT)
    """

"""
#from rest_framework.views import APIView

class PostList(APIView):
    '''
    This class-based view provides an API endpoint for listing and creating posts.
    '''
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer
    def get(request, self):
        '''
        Retrieve all posts.
        '''
        posts = Post.objects.filter(status=True)
        serializer = PostSerializer(posts,many=True)
        return Response(serializer.data)
    def post(self, request):
        '''
        Create a new post.
        '''
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
class PostDetail(APIView):
    '''
    This class-based view provides an API endpoint for retrieving, updating, and deleting posts.
    '''
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer
    def get(self, request, id):
        '''
        Retrieve a specific post.
        '''
        post = get_object_or_404(Post,pk=id,status=True)
        serializer = self.serializer_class(post)
        return Response(serializer.data)
    def put(self, request, id):
        '''
        Update a specific post.
        '''
        post = get_object_or_404(Post,pk=id,status=True)
        serializer = self.serializer_class(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self, request, id):
        '''
        Delete a specific post.
        '''
        post = get_object_or_404(Post,pk=id,status=True)
        post.delete()
        return Response({"detail": "Your post has been successfully removed."},status=status.HTTP_204_NO_CONTENT)
"""
"""
class PostList(ListCreateAPIView):
    '''
    This class-based view provides an API endpoint for listing and creating posts.
    '''
    queryset = Post.objects.filter(status=True)
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class PostDetail(RetrieveUpdateDestroyAPIView):
    '''
    This class-based view provides an API endpoint for retrieving, updating, and deleting posts.
    '''
    lookup_field = 'id'
    queryset = Post.objects.filter(status=True)
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Your post has been successfully removed."},status=status.HTTP_204_NO_CONTENT)
"""

class PostModelViewSet(ModelViewSet):
    '''
    This class-based view provides an API endpoint for listing,
    creating, retrieving, updating, and deleting posts.
    '''
    queryset = Post.objects.filter(status=True)
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    @action(detail=False,methods=['get'])
    def get_ok(self,request):
        return Response({"detail": "API is working correctly."}, status=status.HTTP_200_OK)
        
    
class CategoryModelViewSet(ModelViewSet):
    '''
    This class-based view provides an API endpoint for listing,
    creating, retrieving, updating, and deleting categories.
    '''
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]