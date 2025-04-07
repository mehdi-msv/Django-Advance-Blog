from rest_framework.routers import DefaultRouter
from . import views

app_name = "api-v1"

router = DefaultRouter()
router.register("post", views.PostModelViewSet, basename="post")
router.register("category", views.CategoryModelViewSet, basename="category")
urlpatterns = router.urls


# post_list = views.PostViewSet.as_view({'get': 'list','post': 'create'})
# post_detail = views.PostViewSet.as_view({'get': 'retrieve','put': 'update', 'patch': 'partial_update' , 'delete': 'destroy'})
# urlpatterns = [
#     # path('posts/',views.postList,name='post-list'),
#     # path('post/<int:id>/',views.postDetail,name='post-detail'),
#     path('posts/', post_list, name='posts-list'),
#     path('post/<int:pk>/', post_detail, name='post-detail'),

# ]
