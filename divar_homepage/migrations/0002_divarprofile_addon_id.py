# Generated by Django 5.0.1 on 2024-02-01 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("divar_homepage", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="divarprofile",
            name="addon_id",
            field=models.CharField(max_length=500, null=True),
        ),
    ]