from django.db import migrations, models

import apps.doctors.validators


class Migration(migrations.Migration):

    dependencies = [
        ("consultations", "0011_consultationrequest_full_face_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="consultationrequest",
            name="front_face_image",
            field=models.ImageField(
                blank=True,
                upload_to="consultations/",
                validators=[
                    apps.doctors.validators.validate_image_size,
                    apps.doctors.validators.validate_image_extension,
                ],
                verbose_name="عکس تمام رخ شما",
            ),
        ),
        migrations.AlterField(
            model_name="consultationrequest",
            name="full_face_image",
            field=models.ImageField(
                blank=True,
                upload_to="consultations/",
                validators=[
                    apps.doctors.validators.validate_image_size,
                    apps.doctors.validators.validate_image_extension,
                ],
                verbose_name="عکس نیم رخ شما",
            ),
        ),
    ]
