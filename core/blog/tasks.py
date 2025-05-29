from celery import shared_task
from .models import Comment, Post
from accounts.models import Profile

@shared_task
def create_comment_task(post_slug, profile_id, text, parent_id=None):
    post = Post.objects.get(slug=post_slug)
    author = Profile.objects.get(id=profile_id)

    comment = Comment(post=post, author=author, text=text)

    if parent_id:
        parent_comment = Comment.objects.get(id=parent_id)
        comment.parent = parent_comment

    if author.can_post_directly():
        comment.is_approved = True
    else:
        comment.is_approved = False
    
    comment.flag_if_inappropriate()
    comment.save()
