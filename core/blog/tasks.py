from celery import shared_task
from django.utils import timezone
from .models import Comment, Post
from accounts.models import Profile


@shared_task
def create_comment_task(post_slug, profile_id, text, parent_id=None):
    # Filter posts that are published and active
    posts = Post.objects.filter(
        status=True, published_date__lte=timezone.now()
    )

    # Get the target post by slug
    post = posts.get(slug=post_slug)

    if post:
        # Get the author's profile
        author = Profile.objects.get(id=profile_id)

        # Create the comment instance
        comment = Comment(post=post, author=author, text=text)

        # If it's a reply to another comment, set the parent
        if parent_id:
            parent_comment = Comment.objects.get(id=parent_id)
            comment.parent = parent_comment

        # Check if the user can post without approval
        if author.can_post_directly():
            comment.is_approved = True
        else:
            comment.is_approved = False

        # Automatically flag the comment if it contains inappropriate content
        comment.flag_if_inappropriate()

        # Save the comment to the database
        comment.save()
