import django.core.validators
from django.db import migrations, models

import apps.doctors.validators


class Migration(migrations.Migration):

    dependencies = [
        ("consultations", "0003_add_medical_and_medication_history"),
    ]

    operations = [
        migrations.AddField(
            model_name="consultationrequest",
            name="patient_image",
            field=models.ImageField(
                blank=True,
                upload_to="consultations/",
                validators=[
                    apps.doctors.validators.validate_image_size,
                    apps.doctors.validators.validate_image_extension,
                ],
                verbose_name="عکس",
            ),
        ),
        migrations.AddField(
            model_name="consultationrequest",
            name="referral_source",
            field=models.CharField(
                choices=[
                    ("instagram", "اینستاگرام"),
                    ("telegram", "تلگرام"),
                    ("google", "جست‌وجوی گوگل"),
                    ("friend", "معرفی دوستان و آشنایان"),
                    ("doctor", "معرفی پزشک دیگر"),
                    ("other", "سایر"),
                ],
                default="other",
                max_length=20,
                verbose_name="نحوه آشنایی",
            ),
        ),
        migrations.AddField(
            model_name="consultationrequest",
            name="surgery_details",
            field=models.TextField(blank=True, verbose_name="نوع عمل جراحی"),
        ),
    ]