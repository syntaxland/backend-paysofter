# Generated by Django 3.2.20 on 2024-07-26 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payout', '0003_auto_20231118_1337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payout',
            name='payout_id',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
    ]