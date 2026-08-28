import re

from django import forms
from django.core.exceptions import ValidationError

from .models import ConsultationRequest

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


class ConsultationRequestForm(forms.ModelForm):
    class Meta:
        model = ConsultationRequest
        fields = ("name", "phone", "email", "message")
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "glass-input",
                    "placeholder": "نام و نام خانوادگی",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "glass-input",
                    "placeholder": "۰۹۱۲۳۴۵۶۷۸۹",
                    "dir": "ltr",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "glass-input",
                    "placeholder": "example@email.com",
                    "dir": "ltr",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "glass-input glass-textarea",
                    "placeholder": "پیام خود را بنویسید...",
                    "rows": 4,
                }
            ),
        }
        labels = {
            "name": "نام",
            "phone": "شماره تماس",
            "email": "ایمیل",
            "message": "پیام",
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = re.sub(r"\D", "", phone)
        if len(digits) < 10 or len(digits) > 15:
            raise ValidationError("شماره تماس معتبر نیست.")
        return phone

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise ValidationError("نام باید حداقل ۲ کاراکتر باشد.")
        return name
