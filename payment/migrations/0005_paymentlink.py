# Generated by Django 3.2.20 on 2024-08-15 07:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0004_alter_payoutpayment_total_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer_name', models.CharField(blank=True, max_length=225, null=True)),
                ('buyer_email', models.CharField(blank=True, max_length=225, null=True)),
                ('buyer_phone', models.CharField(blank=True, max_length=225, null=True)),
                ('payment_name', models.CharField(blank=True, max_length=225, null=True)),
                ('payment_link', models.CharField(max_length=50, null=True, unique=True)),
                ('payment_qrcode', models.ImageField(blank=True, null=True, upload_to='payment/qr_codes/')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=16, null=True)),
                ('currency', models.CharField(blank=True, max_length=3, null=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('payout_status', models.BooleanField(default=False)),
                ('is_success', models.BooleanField(default=False)),
                ('payment_id', models.CharField(max_length=50, null=True, unique=True)),
                ('transaction_id', models.CharField(max_length=50, null=True, unique=True)),
                ('payment_method', models.CharField(blank=True, max_length=50, null=True)),
                ('payment_provider', models.CharField(max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('seller', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment_link_seller', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]