from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import Post, Comment, Category


class PostForm(forms.ModelForm):

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    new_category = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "e.g., Technology"}
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        new_category = cleaned_data.get("new_category")

        if not category and not new_category:
            raise forms.ValidationError(
                "You must either select a category or enter a new one."
            )

        if category and new_category:
            raise forms.ValidationError(
                "Please only select one option: either choose from the list or write a new category."
            )

        return cleaned_data

    class Meta:
        model = Post
        fields = [
            "title",
            "image",
            "content",
            "category",
            "status",
            "published_date",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Post title"}
            ),
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control-file"}
            ),
            "content": CKEditorUploadingWidget(),
            "published_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text", "post", "parent"]
        widgets = {
            "post": forms.HiddenInput(),
            "parent": forms.HiddenInput(),
        }
