import os
from pathlib import Path

from django.core.exceptions import ValidationError

MAX_IMAGE_SIZE = 5 * 1024 * 1024


def validate_image_size(value):
    if value.size > MAX_IMAGE_SIZE:
        raise ValidationError("حجم فایل نباید بیشتر از ۵ مگابایت باشد.")


def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    allowed = {".jpg", ".jpeg", ".png", ".webp"}
    if ext not in allowed:
        raise ValidationError("فرمت تصویر مجاز نیست. (jpg, png, webp)")
