# Generated by Django 3.2.20 on 2024-03-20 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promise', '0033_paysofterpromise_modified'),
    ]

    operations = [
        migrations.AddField(
            model_name='paysofterpromise',
            name='promise_msg',
            field=models.TextField(blank=True, max_length=225, null=True),
        ),
    ]