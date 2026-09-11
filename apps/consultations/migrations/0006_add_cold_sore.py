from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("consultations", "0005_add_tobacco_use"),
    ]

    operations = [
        migrations.AddField(
            model_name="consultationrequest",
            name="cold_sore",
            field=models.CharField(
                choices=[("yes", "بله"), ("no", "خیر")],
                default="no",
                max_length=3,
                verbose_name="تبخال",
            ),
        ),
    ]