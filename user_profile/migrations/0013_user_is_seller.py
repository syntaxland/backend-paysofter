# Generated by Django 3.2.20 on 2023-11-24 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0012_user_is_terms_conditions_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_seller',
            field=models.BooleanField(default=False),
        ),
    ]
