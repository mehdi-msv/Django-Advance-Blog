from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "category", "status", "published_date"]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text", "post", "parent"]
        widgets = {
            "post": forms.HiddenInput(),
            "parent": forms.HiddenInput(),
        }
