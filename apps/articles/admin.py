from django.contrib import admin
from django.utils.html import format_html

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "is_published",
        "cover_preview",
        "created_at",
    )
    list_filter = ("is_published", "author", "created_at")
    search_fields = ("title", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "cover_preview_large")
    list_editable = ("is_published",)
    autocomplete_fields = ("author",)
    fieldsets = (
        (
            "محتوا",
            {
                "fields": (
                    "title",
                    "slug",
                    "excerpt",
                    "content",
                )
            },
        ),
        (
            "تصویر",
            {"fields": ("cover_image", "cover_preview_large")},
        ),
        (
            "انتشار",
            {
                "fields": (
                    "author",
                    "is_published",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description="پیش‌نمایش")
    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:8px;" />',
                obj.cover_image.url,
            )
        return "—"

    @admin.display(description="تصویر شاخص")
    def cover_preview_large(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height:200px;border-radius:12px;" />',
                obj.cover_image.url,
            )
        return "—"
