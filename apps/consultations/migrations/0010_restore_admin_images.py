from django.db import migrations, models

import apps.doctors.validators


class Migration(migrations.Migration):

    dependencies = [
        ("consultations", "0009_remove_extra_admin_images"),
    ]

    operations = [
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
