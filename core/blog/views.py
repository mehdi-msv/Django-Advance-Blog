from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
)
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Post, Comment
from accounts.models import Profile
from .forms import PostForm, CommentForm

# Create your views here.

@method_decorator(cache_page(60 * 5), name="dispatch")
class PostListView(ListView):
    """
    This is a class-based view to show list of posts.
    """
    queryset = Post.objects.filter(status=True, published_date__lte=timezone.now())
    context_object_name = "posts"
    ordering = "-published_date"
    paginate_by = 6


class PostDetailView(LoginRequiredMixin, DetailView):
    """
    This is a class-based view to show detail page of a post.
    """

    queryset = Post.objects.filter(status=True, published_date__lte=timezone.now())
    context_object_name = (
        "post"  # for using post instead of object in template
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        context["comments"] = Comment.objects.filter(
            post=post,
            parent__isnull=True,
            is_hidden=False,
            is_approved=True
        ).prefetch_related("replies")

        context["form"] = CommentForm(initial={"post": post})
        return context

class CommentCreateView(LoginRequiredMixin, CreateView):
    """
    This is a class-based view to create a new comment.
    """

    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user.profile

        parent_id = self.request.POST.get("parent")

        form.instance.post = get_object_or_404(Post, slug=self.kwargs['post_slug'])

        if parent_id:
            form.instance.parent = get_object_or_404(Comment, id=parent_id)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:post-detail", kwargs={"slug": self.object.post.slug})


class PostCreateView(LoginRequiredMixin, CreateView):
    """
    This is a class-based view to create a new post.
    """

    model = Post
    form_class = PostForm
    success_url = "/blog/posts/"

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.instance.author = Profile.objects.get(user=self.request.user)
        return super(PostCreateView, self).form_valid(form)


class PostEditView(LoginRequiredMixin, UpdateView):
    """
    This is a class-based view to edit an existing post.
    """

    model = Post
    form_class = PostForm
    success_url = "/blog/posts"

    def get_queryset(self):
        return Post.objects.filter(author__user=self.request.user)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """
    This is a class-based view to delete an existing post.
    """

    model = Post
    success_url = "/blog/posts/"

    def get_queryset(self):
        return Post.objects.filter(author__user=self.request.user)
