from django.db import models
from django.urls import reverse
from django.utils.text import slugify


# Create your models here.


class Post(models.Model):
    """
    This is a class to define posts for blog app
    """

    author = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True)
    category = models.ForeignKey(
        "Category", on_delete=models.SET_NULL, null=True
    )
    title = models.CharField(max_length=256)
    content = models.TextField()
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

    def __str__(self):
        return self.title

    def get_snippet(self):
        return self.content[0:5]

    def get_absolute_api_url(self):
        return reverse("blog:api-v1:post-detail", kwargs={"pk": self.pk})


class Category(models.Model):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def get_absolute_api_url(self):
        return reverse("blog:api-v1:category-detail", kwargs={"pk": self.pk})


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
    
    def __str__(self):
        return f"{self.author} - {self.text[:10]}"
