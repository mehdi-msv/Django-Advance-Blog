from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
)
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseNotAllowed
from accounts.models import Profile
from .tasks import create_comment_task
from .models import Post, Comment, CommentReport
from .forms import PostForm, CommentForm
from .permissions import VerifiedUserRequiredMixin
# Create your views here.

@method_decorator(cache_page(60 * 5), name="dispatch")
class PostListView(ListView):
    """
    This is a class-based view to show list of posts.
    """
    queryset = Post.objects.filter(status=True, published_date__lte=timezone.now())
    context_object_name = "posts"
    ordering = "-published_date"
    paginate_by = 4


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

class CommentCreateView(LoginRequiredMixin, VerifiedUserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            post_slug = self.kwargs.get("slug")
            profile_id = request.user.profile.id
            text = form.cleaned_data["text"]
            parent_id = request.POST.get("parent") or None

            create_comment_task.delay(post_slug, profile_id, text, parent_id)
            messages.success(request, "Your comment has been submitted and is awaiting approval.")
        else:
            messages.error(request, "There was an error submitting your comment. Please try again.")

        return redirect("blog:post-detail", slug=self.kwargs["slug"])

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'])


class CommentReportView(LoginRequiredMixin, VerifiedUserRequiredMixin, View):
    def get(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        user_profile = request.user.profile

        if comment.author == user_profile:
            messages.warning(request, "You cannot report your own comment.")
        else:
            already_reported = CommentReport.objects.filter(user=user_profile, comment=comment).exists()
            if not already_reported:
                CommentReport.objects.create(user=user_profile, comment=comment)
                comment.report()
                messages.success(request, "Report submitted successfully.")
            else:
                messages.info(request, "You have already reported this comment.")

        return redirect("blog:post-detail", slug=comment.post.slug)


# class PostCreateView(LoginRequiredMixin, CreateView):
#     """
#     This is a class-based view to create a new post.
#     """

#     model = Post
#     form_class = PostForm
#     success_url = "/blog/posts/"

#     def form_valid(self, form):
#         # This method is called when valid form data has been POSTed.
#         # It should return an HttpResponse.
#         form.instance.author = Profile.objects.get(user=self.request.user)
#         return super(PostCreateView, self).form_valid(form)


# class PostEditView(LoginRequiredMixin, UpdateView):
#     """
#     This is a class-based view to edit an existing post.
#     """

#     model = Post
#     form_class = PostForm
#     success_url = "/blog/posts"

#     def get_queryset(self):
#         return Post.objects.filter(author__user=self.request.user)


# class PostDeleteView(LoginRequiredMixin, DeleteView):
#     """
#     This is a class-based view to delete an existing post.
#     """

#     model = Post
#     success_url = "/blog/posts/"

#     def get_queryset(self):
#         return Post.objects.filter(author__user=self.request.user)
