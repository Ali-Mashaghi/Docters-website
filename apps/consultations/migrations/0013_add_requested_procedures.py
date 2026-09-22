from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("consultations", "0012_consultationrequest_front_face_image_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="consultationrequest",
            name="requested_procedures",
            field=models.TextField(blank=True, verbose_name="عمل درخواستی"),
        ),
    ]