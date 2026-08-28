from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from apps.articles.models import Article
from apps.doctors.models import Doctor


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
