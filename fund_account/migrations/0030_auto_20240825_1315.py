# Generated by Django 3.2.20 on 2024-08-25 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fund_account', '0029_testdebitaccountfund_buyer_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundaccount',
            name='reference_id',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='fundusdaccount',
            name='reference_id',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
    ]
