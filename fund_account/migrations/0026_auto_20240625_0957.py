# Generated by Django 3.2.20 on 2024-06-25 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fund_account', '0025_delete_currencychoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundaccountcreditcard',
            name='expiration_month',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='fundaccountcreditcard',
            name='expiration_year',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
