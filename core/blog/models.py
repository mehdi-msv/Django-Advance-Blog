from django.db import models
from django.urls import reverse
from django.utils.text import slugify
import re
from decouple import config
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.
def get_bad_words():
    return config("BAD_WORDS", default="").split(",")

URL_PATTERN = re.compile(r'(https?://\S+|www\.\S+)', re.IGNORECASE)

class Post(models.Model):
    """
    This is a class to define posts for blog app
    """

    author = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE, related_name="posts")
    image = models.ImageField(
        upload_to='post_images/',
        blank=True,
        null=True,
        default='defaults/default_post.png'
    )
    category = models.ForeignKey(
        "Category", on_delete=models.SET_NULL, null=True
    )
    title = models.CharField(max_length=256)
    content = RichTextUploadingField()
    status = models.BooleanField()
    slug = models.SlugField(unique=True, blank=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_snippet(self):
        words = self.content.split()
        snippet = " ".join(words[:10])
        return snippet + "..." if len(words) > 10 else snippet

    def get_absolute_api_url(self):
        return reverse("blog:api-v1:post-detail", kwargs={"slug": self.slug})
    
    def __str__(self):
        return self.title


class Category(models.Model):

    name = models.CharField(max_length=50, unique=True)

    def get_absolute_api_url(self):
        return reverse("blog:api-v1:category-detail", kwargs={"name": self.name})
    
    def __str__(self):
        return self.name


class Comment(models.Model):
    author = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE)
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    text = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    is_approved = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    report_count = models.PositiveIntegerField(default=0)
    is_flagged_by_system = models.BooleanField(default=False)
    
    def flag_if_inappropriate(self):
        inappropriate_keywords = get_bad_words()
        text_lower = self.text.lower()
        if any(
            keyword in text_lower for keyword in inappropriate_keywords or
            URL_PATTERN.search(text_lower)
            ):
            self.is_flagged_by_system = True
            self.is_hidden = True
            
    def report(self):
        self.report_count += 1
        self.author.decrease_score(5)
        if self.report_count >= 5:
            self.is_hidden = True
        self.save()

    def __str__(self):
        return f"{self.author} - {self.text[:10]}"


class CommentReport(models.Model):
    user = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE)
    comment = models.ForeignKey("Comment", on_delete=models.CASCADE)
    reported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "comment")

    def __str__(self):
        return f"{self.user} -> {self.comment}"
    