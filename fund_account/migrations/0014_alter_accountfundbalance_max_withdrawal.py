# Generated by Django 3.2.20 on 2023-11-08 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fund_account', '0013_alter_accountfundbalance_max_withdrawal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountfundbalance',
            name='max_withdrawal',
            field=models.DecimalField(blank=True, choices=[(10000, 'Less than 10,000'), (100000, 'Less than 100,000'), (1000000, 'Less than 1,000,000'), (2000000, 'Less than 2,000,000'), (5000000, 'Less than 5,000,000'), (10000000, 'Less than 10,000,000'), (1000000000, 'More than 10,000,000')], decimal_places=2, default=2000000, max_digits=16, null=True),
        ),
    ]
