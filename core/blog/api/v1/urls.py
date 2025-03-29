from django.urls import path,include
from . import views


app_name = 'api-v1'


urlpatterns = [
    # path('posts/',views.postList,name='post-list'),
    # path('post/<int:id>/',views.postDetail,name='post-detail'),
    path('posts/',views.PostList.as_view(),name='posts-list'),
    path('post/<int:id>/',views.PostDetail.as_view(),name='post-detail'),

]