# Generated by Django 3.2.20 on 2024-02-10 12:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrencyChoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(blank=True, choices=[('NGN', 'Nigerian Naira'), ('USD', 'United States Dollar'), ('GBP', 'British Pound Sterling'), ('EUR', 'Euro'), ('JPY', 'Japanese Yen'), ('CAD', 'Canadian Dollar'), ('AUD', 'Australian Dollar'), ('INR', 'Indian Rupee'), ('CNY', 'Chinese Yuan'), ('ZAR', 'South African Rand'), ('BRL', 'Brazilian Real'), ('KES', 'Kenyan Shilling'), ('GHS', 'Ghanaian Cedi'), ('AED', 'United Arab Emirates Dirham'), ('SAR', 'Saudi Riyal'), ('GBP', 'British Pound Sterling')], max_length=3, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='selected_currency_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
