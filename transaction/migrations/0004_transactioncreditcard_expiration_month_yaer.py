# Generated by Django 3.2.20 on 2023-09-23 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0003_transactioncreditcard_expiration_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactioncreditcard',
            name='expiration_month_yaer',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
