from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from apps.articles.models import Article
from apps.consultations.models import ConsultationRequest
from apps.doctors.models import Doctor, Portfolio


class ConsultationRecordForm(forms.ModelForm):
    class Meta:
        model = ConsultationRequest
        fields = (
            "admin_notes",
            "admin_image_1",
            "admin_image_2",
            "admin_image_3",
            "admin_image_4",
        )
        widgets = {
            "admin_notes": forms.Textarea(
                attrs={
                    "class": "glass-input glass-textarea",
                    "rows": 5,
                    "placeholder": "یادداشت یا جزئیات تکمیلی پرونده را بنویسید...",
                }
            ),
            "admin_image_1": forms.ClearableFileInput(
                attrs={"accept": "image/jpeg,image/png,image/webp"}
            ),
            "admin_image_2": forms.ClearableFileInput(
                attrs={"accept": "image/jpeg,image/png,image/webp"}
            ),
            "admin_image_3": forms.ClearableFileInput(
                attrs={"accept": "image/jpeg,image/png,image/webp"}
            ),
            "admin_image_4": forms.ClearableFileInput(
                attrs={"accept": "image/jpeg,image/png,image/webp"}
            ),
        }


class StaffUserCreateForm(forms.ModelForm):
    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={"class": "glass-input", "dir": "ltr"}),
    )
    password_confirm = forms.CharField(
        label="تکرار رمز عبور",
        widget=forms.PasswordInput(attrs={"class": "glass-input", "dir": "ltr"}),
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "glass-input", "dir": "ltr", "placeholder": "username"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "glass-input", "dir": "ltr", "placeholder": "email@example.com"}
            ),
            "first_name": forms.TextInput(
                attrs={"class": "glass-input", "placeholder": "نام"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "glass-input", "placeholder": "نام خانوادگی"}
            ),
        }
        labels = {
            "username": "نام کاربری",
            "email": "ایمیل",
            "first_name": "نام",
            "last_name": "نام خانوادگی",
        }

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("این نام کاربری قبلاً ثبت شده است.")
        return username

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        password_confirm = cleaned.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise ValidationError({"password_confirm": "رمز عبور و تکرار آن یکسان نیست."})

        if password:
            user_data = {
                k: v
                for k, v in cleaned.items()
                if k in ("username", "email", "first_name", "last_name")
            }
            validate_password(password, User(**user_data))

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_staff = True
        user.is_superuser = False
        if commit:
            user.save()
        return user


class DoctorAssignmentForm(forms.Form):
    doctors = forms.ModelMultipleChoiceField(
        queryset=Doctor.objects.filter(is_active=True).order_by("name"),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-list"}),
        required=False,
        label="پزشکان",
    )


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = (
            "title",
            "slug",
            "excerpt",
            "content",
            "cover_image",
            "is_published",
        )
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "glass-input", "placeholder": "عنوان مقاله"}
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "glass-input",
                    "placeholder": "خالی بگذارید تا خودکار ساخته شود",
                    "dir": "ltr",
                }
            ),
            "excerpt": forms.Textarea(
                attrs={
                    "class": "glass-input glass-textarea",
                    "rows": 3,
                    "placeholder": "خلاصه کوتاه مقاله",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "glass-input glass-textarea",
                    "rows": 12,
                    "placeholder": "متن کامل مقاله",
                }
            ),
            "cover_image": forms.ClearableFileInput(
                attrs={"class": "glass-input"}
            ),
            "is_published": forms.CheckboxInput(
                attrs={"class": "checkbox-input"}
            ),
        }
        labels = {
            "title": "عنوان",
            "slug": "اسلاگ",
            "excerpt": "خلاصه",
            "content": "متن مقاله",
            "cover_image": "تصویر شاخص",
            "is_published": "منتشر شده",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        if not self.instance.pk:
            self.fields["is_published"].initial = True

    def clean_slug(self):
        slug = self.cleaned_data.get("slug", "").strip()
        title = self.cleaned_data.get("title", "")
        if not slug:
            slug = slugify(title, allow_unicode=True)
        if not slug:
            raise ValidationError("اسلاگ معتبر نیست.")

        qs = Article.objects.filter(slug=slug)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("این اسلاگ قبلاً استفاده شده است.")

        return slug


class DoctorForm(forms.ModelForm):
    SPECIALTY_CHOICES = (
        ("جراح فک و صورت", "جراح فک و صورت"),
        ("دندان پزشکی", "دندان پزشکی"),
        ("سایر", "سایر"),
    )

    specialty = forms.ChoiceField(
        choices=SPECIALTY_CHOICES,
        label="تخصص",
        widget=forms.Select(attrs={"class": "glass-input"}),
    )

    class Meta:
        model = Doctor
        fields = (
            "name",
            "slug",
            "specialty",
            "bio",
            "profile_image",
            "phone",
            "is_active",
        )
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "glass-input", "placeholder": "نام پزشک"}
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "glass-input",
                    "placeholder": "خالی بگذارید تا خودکار ساخته شود",
                    "dir": "ltr",
                }
            ),
            "specialty": forms.TextInput(
                attrs={"class": "glass-input", "placeholder": "تخصص"}
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "glass-input glass-textarea",
                    "rows": 6,
                    "placeholder": "معرفی و سوابق پزشک",
                }
            ),
            "profile_image": forms.ClearableFileInput(
                attrs={"class": "glass-input"}
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "glass-input",
                    "placeholder": "09123456789",
                    "dir": "ltr",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "checkbox-input"}),
        }
        labels = {
            "name": "نام",
            "slug": "اسلاگ",
            "specialty": "تخصص",
            "bio": "معرفی",
            "profile_image": "تصویر پروفایل",
            "phone": "تلفن",
            "is_active": "فعال",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        if self.instance.pk:
            self.fields["profile_image"].required = False
        if not self.instance.pk:
            self.fields["is_active"].initial = True

    def clean_slug(self):
        slug = self.cleaned_data.get("slug", "").strip()
        name = self.cleaned_data.get("name", "")
        if not slug:
            slug = slugify(name, allow_unicode=True)
        if not slug:
            raise ValidationError("اسلاگ معتبر نیست.")

        qs = Doctor.objects.filter(slug=slug)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("این اسلاگ قبلاً استفاده شده است.")

        return slug


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ("title", "description", "image")
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "glass-input", "placeholder": "عنوان نمونه‌کار"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "glass-input glass-textarea",
                    "rows": 2,
                    "placeholder": "توضیحات (اختیاری)",
                }
            ),
            "image": forms.ClearableFileInput(attrs={"class": "glass-input"}),
        }
        labels = {
            "title": "عنوان",
            "description": "توضیحات",
            "image": "تصویر",
        }
