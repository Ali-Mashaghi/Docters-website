from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify

from apps.doctors.validators import validate_image_extension, validate_image_size


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان")
    slug = models.SlugField(unique=True, allow_unicode=True, verbose_name="اسلاگ")
    excerpt = models.TextField(max_length=500, verbose_name="خلاصه")
    content = models.TextField(verbose_name="متن مقاله")
    cover_image = models.ImageField(
        upload_to="articles/",
        blank=True,
        verbose_name="تصویر شاخص",
        validators=[validate_image_size, validate_image_extension],
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        verbose_name="نویسنده",
    )
    is_published = models.BooleanField(default=True, verbose_name="منتشر شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)
