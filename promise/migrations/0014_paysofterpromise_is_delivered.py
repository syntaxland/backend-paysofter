# Generated by Django 3.2.20 on 2023-11-15 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promise', '0013_auto_20231114_1226'),
    ]

    operations = [
        migrations.AddField(
            model_name='paysofterpromise',
            name='is_delivered',
            field=models.BooleanField(default=False),
        ),
    ]