from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("consultations", "0002_remove_email_add_personal_details"),
    ]

    operations = [
        migrations.AddField(
            model_name="consultationrequest",
            name="medical_history",
            field=models.TextField(default="", verbose_name="سابقه پزشکی"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="consultationrequest",
            name="surgery_history",
            field=models.CharField(
                choices=[("yes", "بله"), ("no", "خیر")],
                default="no",
                max_length=3,
                verbose_name="سابقه عمل جراحی",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="consultationrequest",
            name="medication_history",
            field=models.TextField(default="", verbose_name="سابقه دارویی"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="consultationrequest",
            name="other_medications",
            field=models.TextField(blank=True, verbose_name="داروهای دیگر"),
        ),
        migrations.AddField(
            model_name="consultationrequest",
            name="substance_use",
            field=models.TextField(default="", verbose_name="مصرف دخانیات و مواد"),
            preserve_default=False,
        ),
    ]