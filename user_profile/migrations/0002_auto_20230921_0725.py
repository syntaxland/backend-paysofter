# Generated by Django 3.2.20 on 2023-09-21 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_live_mode',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='live_api_key',
            field=models.CharField(max_length=64, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='user',
            name='test_api_key',
            field=models.CharField(max_length=64, null=True, unique=True),
        ),
    ]
