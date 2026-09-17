from django.db import migrations, models

import apps.doctors.validators


class Migration(migrations.Migration):

    dependencies = [
        ("consultations", "0010_restore_admin_images"),
    ]

    operations = [
        migrations.AddField(
            model_name="consultationrequest",
            name="full_face_image",
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
    ]
