from django import forms
from .models import Post


class ContactForm(forms.Form):

    name = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "category", "status", "published_date"]
