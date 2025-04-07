from django.contrib import admin
from .models import Post, Category


# Register your models here.
class PostAdmin(admin.ModelAdmin):
    #   Define the fields to be displayed in the admin interface

    list_display = (
        "title",
        "author",
        "category",
        "status",
        "created_date",
        "published_date",
    )
    list_filter = ("author", "category", "status", "published_date")
    search_fields = ("title", "author__email", "category__name", "content")
    ordering = ("-published_date",)


admin.site.register(Post, PostAdmin)
admin.site.register(Category)
