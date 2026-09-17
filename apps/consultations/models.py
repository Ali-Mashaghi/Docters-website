from django.db import models

from apps.doctors.models import Doctor
from apps.doctors.validators import validate_image_extension, validate_image_size


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
    birth_date = models.CharField(
        max_length=10,
        verbose_name="تاریخ تولد",
        help_text="به صورت ۱۴۰۰/۰۱/۰۱",
    )
    job = models.CharField(max_length=150, verbose_name="شغل")
    MARITAL_STATUS_CHOICES = [
        ("single", "مجرد"),
        ("married", "متاهل"),
    ]
    marital_status = models.CharField(
        max_length=10,
        choices=MARITAL_STATUS_CHOICES,
        verbose_name="وضعیت تاهل",
    )
    address = models.TextField(verbose_name="آدرس")
    medical_history = models.TextField(verbose_name="سابقه پزشکی")
    SURGERY_CHOICES = [
        ("yes", "بله"),
        ("no", "خیر"),
    ]
    surgery_history = models.CharField(
        max_length=3,
        choices=SURGERY_CHOICES,
        verbose_name="سابقه عمل جراحی",
    )
    surgery_details = models.TextField(blank=True, verbose_name="نوع عمل جراحی")
    cold_sore = models.CharField(
        max_length=3,
        choices=SURGERY_CHOICES,
        default="no",
        verbose_name="تبخال",
    )
    medication_history = models.TextField(verbose_name="سابقه دارویی")
    other_medications = models.TextField(blank=True, verbose_name="داروهای دیگر")
    substance_use = models.TextField(verbose_name="مصرف دخانیات و مواد")
    REFERRAL_SOURCE_CHOICES = [
        ("instagram", "اینستاگرام"),
        ("telegram", "تلگرام"),
        ("google", "جست‌وجوی گوگل"),
        ("friend", "معرفی دوستان و آشنایان"),
        ("doctor", "معرفی پزشک دیگر"),
        ("other", "سایر"),
    ]
    referral_source = models.CharField(
        max_length=20,
        choices=REFERRAL_SOURCE_CHOICES,
        default="other",
        verbose_name="نحوه آشنایی",
    )
    patient_image = models.ImageField(
        upload_to="consultations/",
        blank=True,
        verbose_name="عکس",
        validators=[validate_image_size, validate_image_extension],
    )
    full_face_image = models.ImageField(
        upload_to="consultations/",
        blank=True,
        verbose_name="عکس نیم رخ شما",
        validators=[validate_image_size, validate_image_extension],
    )
    front_face_image = models.ImageField(
        upload_to="consultations/",
        blank=True,
        verbose_name="عکس تمام رخ شما",
        validators=[validate_image_size, validate_image_extension],
    )
    admin_notes = models.TextField(blank=True, verbose_name="یادداشت مدیر")
    admin_image_1 = models.ImageField(
        upload_to="consultations/admin/",
        blank=True,
        verbose_name="عکس پرونده ۱",
        validators=[validate_image_size, validate_image_extension],
    )
    admin_image_2 = models.ImageField(
        upload_to="consultations/admin/",
        blank=True,
        verbose_name="عکس پرونده ۲",
        validators=[validate_image_size, validate_image_extension],
    )
    admin_image_3 = models.ImageField(
        upload_to="consultations/admin/",
        blank=True,
        verbose_name="عکس پرونده ۳",
        validators=[validate_image_size, validate_image_extension],
    )
    admin_image_4 = models.ImageField(
        upload_to="consultations/admin/",
        blank=True,
        verbose_name="عکس پرونده ۴",
        validators=[validate_image_size, validate_image_extension],
    )
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
