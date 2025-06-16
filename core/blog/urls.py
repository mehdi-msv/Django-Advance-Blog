from django.urls import path, include
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post-list"),
    path(
        "post/<str:slug>/", views.PostDetailView.as_view(), name="post-detail"
    ),
    path(
        "post/<str:slug>/comment/",
        views.CommentCreateView.as_view(),
        name="post-comment",
    ),
    path(
        "comment/<int:pk>/report/",
        views.CommentReportView.as_view(),
        name="report-comment",
    ),
    path("create/", views.PostCreateView.as_view(), name="post-create"),
    path(
        "post/<str:slug>/edit/",
        views.PostEditView.as_view(),
        name="post-edit",
    ),
    path(
        "post/<str:slug>/delete/",
        views.PostDeleteView.as_view(),
        name="post-delete",
    ),
    path("api/v1/", include("blog.api.v1.urls")),
]
