from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("consultations", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="consultationrequest",
            name="email",
        ),
        migrations.AddField(
            model_name="consultationrequest",
            name="address",
            field=models.TextField(default="", verbose_name="آدرس"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="consultationrequest",
            name="birth_date",
            field=models.CharField(
                default="",
                help_text="به صورت ۱۴۰۰/۰۱/۰۱",
                max_length=10,
                verbose_name="تاریخ تولد",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="consultationrequest",
            name="job",
            field=models.CharField(default="", max_length=150, verbose_name="شغل"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="consultationrequest",
            name="marital_status",
            field=models.CharField(
                choices=[("single", "مجرد"), ("married", "متاهل")],
                default="single",
                max_length=10,
                verbose_name="وضعیت تاهل",
            ),
            preserve_default=False,
        ),
    ]