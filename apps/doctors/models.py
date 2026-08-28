from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify

from .validators import validate_image_extension, validate_image_size


class Doctor(models.Model):
    name = models.CharField(max_length=150, verbose_name="نام")
    slug = models.SlugField(unique=True, allow_unicode=True, verbose_name="اسلاگ")
    specialty = models.CharField(max_length=150, verbose_name="تخصص")
    bio = models.TextField(verbose_name="معرفی")
    profile_image = models.ImageField(
        upload_to="doctors/",
        verbose_name="تصویر پروفایل",
        validators=[validate_image_size, validate_image_extension],
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name="تلفن")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "پزشک"
        verbose_name_plural = "پزشکان"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Portfolio(models.Model):
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="portfolios",
        verbose_name="پزشک",
    )
    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    image = models.ImageField(
        upload_to="portfolio/",
        verbose_name="تصویر",
        validators=[validate_image_size, validate_image_extension],
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "نمونه‌کار"
        verbose_name_plural = "نمونه‌کارها"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} — {self.doctor.name}"


class DoctorManager(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="doctor_permissions",
        verbose_name="کاربر",
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="managers",
        verbose_name="پزشک",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "مدیر پزشک"
        verbose_name_plural = "مدیران پزشک"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "doctor"],
                name="unique_user_doctor",
            )
        ]

    def __str__(self):
        return f"{self.user.username} → {self.doctor.name}"
