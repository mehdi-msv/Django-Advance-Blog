from django.urls import path, include
from . import views

app_name = "blog"

urlpatterns = [
    path("index/", views.IndexView.as_view(), name="index"),
    path(
        "redirect-to-django/<int:pk>/",
        views.RedirectToDjango.as_view(),
        name="redirect-to-django",
    ),
    path("post/", views.PostListView.as_view(), name="post-list"),
    path(
        "post/list/api/",
        views.PostListAPIView.as_view(),
        name="post-list-api",
    ),
    path(
        "post/<int:pk>/", views.PostDetailView.as_view(), name="post-detail"
    ),
    path("contact/", views.ContactView.as_view(), name="contact-us"),
    path("create/", views.PostCreateView.as_view(), name="post-create"),
    path(
        "post/<int:pk>/edit/", views.PostEditView.as_view(), name="post-edit"
    ),
    path(
        "post/<int:pk>/delete/",
        views.PostDeleteView.as_view(),
        name="post-delete",
    ),
    path("api/v1/", include("blog.api.v1.urls")),
]

"""+=
    path('fbv-index', views.fbv_index, name='fbv_index'),
    path('cbv-index', TemplateView.as_view(template_name='index.html', extra_context={'name':'mehdi'}),name='cbv_index'),
    path(
         "go-to-django/",
         RedirectView.as_view(url="https://www.djangoproject.com/"),
         name="go-to-django",
     ),
    path(
         'go-to-index',
          RedirectView.as_view(pattern_name='blog:cbv_index'),
          name='go-to-index'
          ),
    path('redirect-to-django2/<int:pk>', views.redirect_to_django, name='redirect_to_django2'),
"""
