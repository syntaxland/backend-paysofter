# Generated by Django 3.2.20 on 2024-02-06 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fund_account', '0022_usdfundaccountcreditcard'),
    ]

    operations = [
        migrations.AddField(
            model_name='debitaccountfund',
            name='new_bal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='debitaccountfund',
            name='old_bal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='debitusdaccountfund',
            name='new_bal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='debitusdaccountfund',
            name='old_bal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='fundaccount',
            name='new_bal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='fundaccount',
            name='old_bal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='fundusdaccount',
            name='new_bal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='fundusdaccount',
            name='old_bal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]