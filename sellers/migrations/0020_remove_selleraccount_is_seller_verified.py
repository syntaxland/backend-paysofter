# Generated by Django 3.2.20 on 2024-08-23 08:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sellers', '0019_selleraccount_business_logo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='selleraccount',
            name='is_seller_verified',
        ),
    ]