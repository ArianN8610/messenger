# Generated by Django 4.2.16 on 2025-02-19 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='last_seen',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
