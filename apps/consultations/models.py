from django.db import models

from apps.doctors.models import Doctor


class ConsultationRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("contacted", "تماس گرفته شد"),
        ("completed", "تکمیل شد"),
        ("cancelled", "لغو شد"),
    ]

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="consultation_requests",
        verbose_name="پزشک",
    )
    name = models.CharField(max_length=150, verbose_name="نام")
    phone = models.CharField(max_length=20, verbose_name="شماره تماس")
    email = models.EmailField(blank=True, verbose_name="ایمیل")
    message = models.TextField(blank=True, verbose_name="پیام")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="وضعیت",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "درخواست مشاوره"
        verbose_name_plural = "درخواست‌های مشاوره"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.doctor.name}"
