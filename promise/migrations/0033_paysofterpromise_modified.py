# Generated by Django 3.2.20 on 2024-03-19 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promise', '0032_auto_20240218_1948'),
    ]

    operations = [
        migrations.AddField(
            model_name='paysofterpromise',
            name='modified',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
