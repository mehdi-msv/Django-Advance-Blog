from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView
)
from django.contrib.auth.mixins import (
    PermissionRequiredMixin
)
from django.utils import timezone
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from accounts.models import Profile
from django.core.cache import cache
from django.db.models import Q
from .tasks import create_comment_task
from .models import Post, Comment, CommentReport, Category
from .forms import PostForm, CommentForm
from .permissions import VerifiedUserRequiredMixin, CustomLoginRequiredMixin
# Create your views here.


class PostListView(ListView):
    context_object_name = "posts"
    ordering = "-published_date"
    paginate_by = 4

    def get_queryset(self):
        key = f"cached_posts_page_{self.request.GET.get('page', 1)}"
        return cache.get_or_set(key, self._get_posts(), 10)

    def _get_posts(self):
        return Post.objects.filter(
            status=True,
            published_date__lte=timezone.now()
        ).order_by('-published_date')


class PostDetailView(CustomLoginRequiredMixin, DetailView):
    """
    Displays the detail page of a single post.
    Only accessible to logged-in users.
    """
    
    context_object_name = "post"  # Use 'post' instead of default 'object' in the template

    def get_context_data(self, **kwargs):
        """
        Adds comments and comment form to the context.
        """
        context = super().get_context_data(**kwargs)
        post = self.object

        # Get approved comments for this post
        context["comments"] = Comment.objects.filter(
            post=post,
            parent__isnull=True,
            is_hidden=False,
            is_approved=True
        ).prefetch_related("replies")  # Optimize for nested replies

        # Provide a comment form with pre-filled post reference
        context["form"] = CommentForm(initial={"post": post})
        return context

    def get_queryset(self):
        return Post.objects.filter(
            Q(status=True, published_date__lte=timezone.now())
            |
            Q(author=self.request.user.profile)
        ).distinct()

class CommentCreateView(CustomLoginRequiredMixin, VerifiedUserRequiredMixin, FormView):
    """
    Handles creation of new comments using a Django FormView.
    Only logged-in and verified users can post comments.
    Uses asynchronous task for comment creation.
    """

    form_class = CommentForm
    http_method_names = ['post']  # Only allow POST requests

    def form_valid(self, form):
        """
        Called when the submitted form is valid.
        Triggers a Celery task to create the comment asynchronously.
        """
        post_slug = self.kwargs.get("slug")
        profile_id = self.request.user.profile.id
        text = form.cleaned_data["text"]
        parent_id = self.request.POST.get("parent") or None

        create_comment_task.delay(post_slug, profile_id, text, parent_id)
        messages.success(self.request, "Your comment has been submitted and is awaiting approval.")
        return redirect("blog:post-detail", slug=post_slug)

    def form_invalid(self, form):
        """
        Called when the submitted form is invalid.
        Displays an error message and redirects back to the post detail page.
        """
        messages.error(self.request, "There was an error submitting your comment. Please check the form and try again.")
        return redirect("blog:post-detail", slug=self.kwargs.get("slug"))


class CommentReportView(CustomLoginRequiredMixin, VerifiedUserRequiredMixin, View):
    """
    Allows users to report inappropriate comments.
    Prevents duplicate reports and self-reporting.
    """

    def get(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        user_profile = request.user.profile

        # Prevent users from reporting their own comment
        if comment.author == user_profile:
            messages.warning(request, "You cannot report your own comment.")
        else:
            # Check if the user has already reported this comment
            already_reported = CommentReport.objects.filter(user=user_profile, comment=comment).exists()
            if not already_reported:
                # Create a new report and trigger any report-related logic
                CommentReport.objects.create(user=user_profile, comment=comment)
                comment.report()  # increments a report count and decreases the author's score
                messages.success(request, "Report submitted successfully.")
            else:
                messages.info(request, "You have already reported this comment.")

        return redirect("blog:post-detail", slug=comment.post.slug)


class PostCreateView(CustomLoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    View to allow authorized users to create a new blog post.
    Only users with the 'blog.add_post' permission are allowed.
    Automatically assigns the logged-in user as the author.
    If the user provides a new category, it will be created and assigned to the post.
    """

    model = Post
    form_class = PostForm
    template_name = "blog/post_create.html"
    permission_required = "blog.add_post"

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to handle unauthorized access (GET or POST).
        Redirects to the post list with an error message if permission is denied.
        """
        if not request.user.has_perm(self.permission_required):
            messages.error(request, "You do not have permission to access this page.")
            return redirect("blog:post-list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Assign the logged-in user as the post's author.
        If a new category is provided by the user, create and assign it.
        """
        new_category = self.request.POST.get("new_category")
        if new_category:
            category_obj, _ = Category.objects.get_or_create(name=new_category)
            form.instance.category = category_obj

        form.instance.author = Profile.objects.get(user=self.request.user)
        messages.success(self.request, "Your post has been created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Handle invalid form submission with an error message.
        """
        messages.error(self.request, "An error occurred while creating the post. Please review the form and try again.")
        return super().form_invalid(form)

    def get_success_url(self):
        """
        Redirect to the user's profile page upon successful post creation.
        """
        return reverse("accounts:profile")


class PostEditView(CustomLoginRequiredMixin, UpdateView):
    """
    A class-based view to edit an existing post.
    Only accessible to the author of the post.
    """
    model = Post
    form_class = PostForm
    template_name = "blog/post_edit.html"
    context_object_name = "post"

    def get_queryset(self):
        # Limit editable posts to those owned by the logged-in user
        return Post.objects.filter(author__user=self.request.user)

    def form_valid(self, form):
        """
        Called when valid form data has been submitted.
        Saves the form and shows a success message.
        """
        messages.success(self.request, "The post was updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Called when the submitted form is invalid.
        Shows an error message.
        """
        messages.error(self.request, "There was an error updating the post. Please try again.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse("blog:post-detail", kwargs={"slug": self.object.slug})


class PostDeleteView(CustomLoginRequiredMixin, DeleteView):
    """
    Handles the deletion of a post by its author.
    Ensures only the owner of the post can delete it.
    Displays a success message upon successful deletion.
    """

    model = Post
    http_method_names = ['post']  # Only allow POST requests
    
    def get_queryset(self):
        # Only allow deletion of posts owned by the logged-in user
        return Post.objects.filter(author__user=self.request.user)

    def delete(self, request, *args, **kwargs):
        """
        Override the default delete method to add a success message.
        """
        post = self.get_object()
        messages.success(request, f"Post '{post.title}' was successfully deleted.")
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        """
        Redirect to the user's profile page upon successful post deletion.
        """
        return reverse("accounts:profile")
