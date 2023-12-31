# Generated by Django 3.2.20 on 2023-09-22 18:51

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
            name='SendSellerEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(blank=True, max_length=255, null=True)),
                ('message', models.TextField(blank=True, max_length=5000, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('paysofter_email', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='paysofter_send_seller_email', to=settings.AUTH_USER_MODEL)),
                ('seller', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='seller', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SendBuyerEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer_email', models.EmailField(blank=True, max_length=255, null=True)),
                ('subject', models.CharField(blank=True, max_length=255, null=True)),
                ('message', models.TextField(blank=True, max_length=5000, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('paysofter_email', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='paysofter_send_buyer_email', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
