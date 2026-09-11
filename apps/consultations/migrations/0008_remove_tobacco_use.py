from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("consultations", "0007_add_admin_case_details"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="consultationrequest",
            name="tobacco_use",
        ),
    ]
