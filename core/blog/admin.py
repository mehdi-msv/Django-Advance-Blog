from django.contrib import admin
from .models import Post, Category
from .models import Comment
from .forms import PostForm


# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    #   Define the fields to be displayed in the admin interface
    form = PostForm

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


@admin.action(
    description="Delete selected comments and decrease author score by 25"
)
def confirm_and_delete_comments(modeladmin, request, queryset):
    for comment in queryset:
        comment.author.decrease_score(25)
        comment.delete()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "post",
        "is_approved",
        "is_hidden",
        "report_count",
        "is_flagged_by_system",
    )
    list_filter = ("is_hidden", "is_flagged_by_system", "is_approved")
    actions = [confirm_and_delete_comments]


admin.site.register(Category)
