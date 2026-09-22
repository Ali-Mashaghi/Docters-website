import re

from django import forms
from django.core.exceptions import ValidationError

from .models import ConsultationRequest

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_SIZE = 50 * 1024 * 1024

MEDICAL_HISTORY_CHOICES = (
    ("heart", "بیماری قلبی"),
    ("thyroid", "تیروئید"),
    ("blood_pressure", "فشار خون"),
    ("diabetes", "دیابت"),
    ("lung", "بیماری ریوی"),
    ("psychiatric", "روان پزشکی"),
    ("seizure", "تشنج یا صرع"),
    ("allergy", "حساسیت و آلرژی"),
    ("none", "هیچکدام"),
)

MEDICATION_HISTORY_CHOICES = (
    ("hormonal", "قرص‌های هورمونی (ال دی یا ضد بارداری)"),
    ("levothyroxine", "لووتیروکسین"),
    ("psychiatric", "قرص‌های روانپزشکی"),
    ("blood_thinner", "قرص‌های رقیق‌کننده خون (هپارین، وارفارین، آسپرین)"),
    ("vitamins", "ویتامین‌های D،A،K،E"),
    ("none", "هیچکدام"),
)

SUBSTANCE_USE_CHOICES = (
    ("cigarette", "سیگار"),
    ("hookah", "قلیان"),
    ("opioids", "مواد مخدر (گل، تریاک، قرص‌های روانگردان و...)"),
    ("alcohol", "مشروب"),
    ("none", "هیچکدام"),
    ("all", "همه موارد"),
)


class ConsultationRequestForm(forms.ModelForm):
    medical_history = forms.MultipleChoiceField(
        choices=MEDICAL_HISTORY_CHOICES,
        label="سابقه پزشکی",
        widget=forms.CheckboxSelectMultiple,
    )
    surgery_history = forms.ChoiceField(
        choices=ConsultationRequest.SURGERY_CHOICES,
        label="آیا سابقه عمل جراحی داشته‌اید؟",
        widget=forms.RadioSelect,
    )
    medication_history = forms.MultipleChoiceField(
        choices=MEDICATION_HISTORY_CHOICES,
        label="موارد بسیار مهم",
        widget=forms.CheckboxSelectMultiple,
    )
    other_medications = forms.CharField(
        label="اگر به جز موارد بالا داروی دیگری استفاده می‌کنید نام ببرید",
        required=False,
        widget=forms.TextInput(attrs={"class": "glass-input"}),
    )
    substance_use = forms.MultipleChoiceField(
        choices=SUBSTANCE_USE_CHOICES,
        label="آیا دخانیات یا مواد مصرف می‌کنید؟",
        widget=forms.CheckboxSelectMultiple,
    )
    surgery_details = forms.CharField(
        label="چه نوع جراحی انجام داده‌اید؟",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "glass-input",
                "placeholder": "در صورت انتخاب بله، نوع جراحی را بنویسید",
            }
        ),
    )
    cold_sore = forms.ChoiceField(
        choices=ConsultationRequest.SURGERY_CHOICES,
        label="آیا تبخال می‌زنید؟",
        widget=forms.RadioSelect,
    )
    referral_source = forms.ChoiceField(
        choices=ConsultationRequest.REFERRAL_SOURCE_CHOICES,
        label="نحوه آشنایی با ما",
        widget=forms.Select(attrs={"class": "glass-input"}),
    )

    class Meta:
        model = ConsultationRequest
        fields = (
            "name",
            "phone",
            "birth_date",
            "job",
            "marital_status",
            "address",
            "medical_history",
            "surgery_history",
            "surgery_details",
            "cold_sore",
            "medication_history",
            "other_medications",
            "substance_use",
            "patient_image",
            "front_face_image",
            "referral_source",
            "message",
        )
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
            "birth_date": forms.TextInput(
                attrs={
                    "id": "birth_date",
                    "class": "glass-input",
                    "placeholder": "۱۴۰۰/۰۱/۰۱",
                    "autocomplete": "off",
                    "data-jdp": "",
                }
            ),
            "job": forms.TextInput(
                attrs={
                    "class": "glass-input",
                    "placeholder": "مثلاً مهندس",
                }
            ),
            "marital_status": forms.Select(attrs={"class": "glass-input"}),
            "address": forms.Textarea(
                attrs={
                    "class": "glass-input glass-textarea",
                    "placeholder": "آدرس",
                    "rows": 3,
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "glass-input glass-textarea",
                    "placeholder": "پیام خود را بنویسید...",
                    "rows": 4,
                }
            ),
            "patient_image": forms.ClearableFileInput(
                attrs={
                    "class": "file-input",
                    "accept": "image/jpeg,image/png,image/webp",
                }
            ),
            "front_face_image": forms.ClearableFileInput(
                attrs={
                    "class": "file-input",
                    "accept": "image/jpeg,image/png,image/webp",
                }
            ),
        }
        labels = {
            "name": "نام و نام خانوادگی",
            "phone": "شماره تماس",
            "birth_date": "تاریخ تولد",
            "job": "شغل",
            "marital_status": "وضعیت تاهل",
            "address": "آدرس به اختصار",
            "medical_history": "سابقه پزشکی",
            "surgery_history": "آیا سابقه عمل جراحی داشته‌اید؟",
            "surgery_details": "چه نوع جراحی انجام داده‌اید؟",
            "cold_sore": "آیا تبخال می‌زنید؟",
            "medication_history": "موارد بسیار مهم",
            "other_medications": "داروهای دیگر",
            "substance_use": "آیا دخانیات یا مواد مصرف می‌کنید؟",
            "referral_source": "نحوه آشنایی با ما",
            "patient_image": "عکس فرم بینی مد نظر شما",
            "front_face_image": "عکس تمام رخ خودتون",
            "message": "پیام",
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.medical_history = self._selected_labels(
            self.cleaned_data["medical_history"], MEDICAL_HISTORY_CHOICES
        )
        instance.medication_history = self._selected_labels(
            self.cleaned_data["medication_history"], MEDICATION_HISTORY_CHOICES
        )
        instance.substance_use = self._selected_labels(
            self.cleaned_data["substance_use"], SUBSTANCE_USE_CHOICES
        )
        if commit:
            instance.save()
        return instance

    @staticmethod
    def _selected_labels(values, choices):
        labels = dict(choices)
        return "، ".join(labels[value] for value in values)

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

    def clean_birth_date(self):
        birth_date = self.cleaned_data["birth_date"].strip()
        if not re.fullmatch(r"[۰-۹0-9]{4}/[۰-۹0-9]{2}/[۰-۹0-9]{2}", birth_date):
            raise ValidationError("تاریخ تولد را به صورت شمسی وارد کنید.")
        return birth_date

    def clean(self):
        cleaned_data = super().clean()

        for field_name in (
            "medical_history",
            "medication_history",
            "substance_use",
        ):
            values = cleaned_data.get(field_name) or []
            if "none" in values and len(values) > 1:
                self.add_error(
                    field_name,
                    "اگر «هیچکدام» را انتخاب می‌کنید، گزینه دیگری نباید انتخاب شود.",
                )

        if cleaned_data.get("surgery_history") == "no":
            cleaned_data["surgery_details"] = ""

        return cleaned_data
