# Generated by Django 3.2.20 on 2023-11-11 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promise', '0006_rename_payer_paysofterpromise_buyer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paysofterpromise',
            name='duration',
            field=models.CharField(blank=True, choices=[('1day', '1 day'), ('2days', 'Less than 2 days'), ('3days', 'Less than 3 days'), ('1week', 'Less than 1 week'), ('2week', 'Less than 2 weeks'), ('1month', 'Less than 1 month')], default='1day', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='paysofterpromise',
            name='payment_method',
            field=models.CharField(blank=True, choices=[('debit_card', 'Debit Card'), ('paysofter_account_fund', 'Paysofter Account Fund'), ('paysofter_promise', 'Paysofter Promise'), ('bank', 'Bank'), ('transfer', 'Transfer'), ('qrcode', 'QR COde'), ('USSD', 'USSD')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='paysofterpromise',
            name='payment_provider',
            field=models.CharField(choices=[('paysofter', 'Paysofter'), ('mastercard', 'Mastercard'), ('verve', 'Verve'), ('visa', 'Visa'), ('gtb', 'GTB'), ('fidelity', 'Fidelity')], max_length=100),
        ),
        migrations.AlterField(
            model_name='paysofterpromise',
            name='status',
            field=models.CharField(blank=True, choices=[('fulfilled', 'Fulfilled'), ('pending', 'Pending'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], max_length=100, null=True),
        ),
    ]