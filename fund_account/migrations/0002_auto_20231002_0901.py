# Generated by Django 3.2.20 on 2023-10-02 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fund_account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fundaccount',
            name='currency',
            field=models.CharField(blank=True, choices=[('NGN', 'Nigerian Naira'), ('USD', 'United States Dollar'), ('GBP', 'British Pound Sterling'), ('EUR', 'Euro'), ('JPY', 'Japanese Yen'), ('CAD', 'Canadian Dollar'), ('AUD', 'Australian Dollar'), ('INR', 'Indian Rupee'), ('CNY', 'Chinese Yuan'), ('ZAR', 'South African Rand'), ('BRL', 'Brazilian Real'), ('KES', 'Kenyan Shilling'), ('GHS', 'Ghanaian Cedi'), ('AED', 'United Arab Emirates Dirham'), ('SAR', 'Saudi Riyal'), ('GBP', 'British Pound Sterling')], max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='fundaccount',
            name='payment_method',
            field=models.CharField(blank=True, choices=[('credit_card', 'Credit Card'), ('bank_transfer', 'Bank Transfer'), ('paypal', 'PayPal'), ('google_pay', 'Google Pay'), ('apple_pay', 'Apple Pay')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='fundaccount',
            name='payment_provider',
            field=models.CharField(choices=[('paypal', 'PayPal'), ('stripe', 'Stripe'), ('paypal', 'PayPal'), ('gtb', 'GTB'), ('fidelity', 'Fidelity')], max_length=50),
        ),
    ]
