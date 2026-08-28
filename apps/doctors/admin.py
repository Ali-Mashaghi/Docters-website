from django.contrib import admin
from django.utils.html import format_html

from .models import Doctor, DoctorManager, Portfolio


class PortfolioInline(admin.TabularInline):
    model = Portfolio
    extra = 1
    fields = ("title", "description", "image")


class DoctorManagerInline(admin.TabularInline):
    model = DoctorManager
    extra = 1
    autocomplete_fields = ("user",)
    verbose_name = "مدیر"
    verbose_name_plural = "مدیران"


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "specialty",
        "is_active",
        "profile_preview",
        "created_at",
    )
    list_filter = ("is_active", "specialty", "created_at")
    search_fields = ("name", "specialty", "bio")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "profile_preview_large")
    inlines = [PortfolioInline, DoctorManagerInline]
    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "name",
                    "slug",
                    "specialty",
                    "bio",
                    "phone",
                    "is_active",
                )
            },
        ),
        (
            "تصویر",
            {"fields": ("profile_image", "profile_preview_large")},
        ),
        ("تاریخ", {"fields": ("created_at",)}),
    )

    @admin.display(description="پیش‌نمایش")
    def profile_preview(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:8px;" />',
                obj.profile_image.url,
            )
        return "—"

    @admin.display(description="تصویر پروفایل")
    def profile_preview_large(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" style="max-height:200px;border-radius:12px;" />',
                obj.profile_image.url,
            )
        return "—"


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("title", "doctor", "image_preview", "created_at")
    list_filter = ("doctor", "created_at")
    search_fields = ("title", "description", "doctor__name")
    autocomplete_fields = ("doctor",)
    readonly_fields = ("created_at", "image_preview_large")

    @admin.display(description="پیش‌نمایش")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:8px;" />',
                obj.image.url,
            )
        return "—"

    @admin.display(description="تصویر")
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:200px;border-radius:12px;" />',
                obj.image.url,
            )
        return "—"


@admin.register(DoctorManager)
class DoctorManagerAdmin(admin.ModelAdmin):
    list_display = ("user", "doctor", "created_at")
    list_filter = ("doctor", "created_at")
    search_fields = ("user__username", "user__email", "doctor__name")
    autocomplete_fields = ("user", "doctor")
