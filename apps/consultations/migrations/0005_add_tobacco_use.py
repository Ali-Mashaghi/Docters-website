from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("consultations", "0004_add_surgery_referral_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="consultationrequest",
            name="tobacco_use",
            field=models.CharField(
                choices=[("yes", "بله"), ("no", "خیر")],
                default="no",
                max_length=3,
                verbose_name="مصرف دخانیات",
            ),
        ),
    ]