from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("consultations", "0008_remove_tobacco_use"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="consultationrequest",
            name="admin_image_3",
        ),
        migrations.RemoveField(
            model_name="consultationrequest",
            name="admin_image_4",
        ),
    ]