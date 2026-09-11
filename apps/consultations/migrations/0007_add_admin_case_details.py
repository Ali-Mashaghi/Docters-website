from django.db import migrations, models

import apps.doctors.validators


class Migration(migrations.Migration):

    dependencies = [
        ("consultations", "0006_add_cold_sore"),
    ]

    operations = [
        migrations.AddField(
            model_name="consultationrequest",
            name="admin_notes",
            field=models.TextField(blank=True, verbose_name="یادداشت مدیر"),
        ),
        migrations.AddField(
            model_name="consultationrequest",
            name="admin_image_1",
            field=models.ImageField(
                blank=True,
                upload_to="consultations/admin/",
                validators=[
                    apps.doctors.validators.validate_image_size,
                    apps.doctors.validators.validate_image_extension,
                ],
                verbose_name="عکس پرونده ۱",
            ),
        ),
        migrations.AddField(
            model_name="consultationrequest",
            name="admin_image_2",
            field=models.ImageField(
                blank=True,
                upload_to="consultations/admin/",
                validators=[
                    apps.doctors.validators.validate_image_size,
                    apps.doctors.validators.validate_image_extension,
                ],
                verbose_name="عکس پرونده ۲",
            ),
        ),
        migrations.AddField(
            model_name="consultationrequest",
            name="admin_image_3",
            field=models.ImageField(
                blank=True,
                upload_to="consultations/admin/",
                validators=[
                    apps.doctors.validators.validate_image_size,
                    apps.doctors.validators.validate_image_extension,
                ],
                verbose_name="عکس پرونده ۳",
            ),
        ),
        migrations.AddField(
            model_name="consultationrequest",
            name="admin_image_4",
            field=models.ImageField(
                blank=True,
                upload_to="consultations/admin/",
                validators=[
                    apps.doctors.validators.validate_image_size,
                    apps.doctors.validators.validate_image_extension,
                ],
                verbose_name="عکس پرونده ۴",
            ),
        ),
    ]
