# Generated by Django 3.2.20 on 2024-02-15 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promise', '0029_alter_paysofterpromise_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='promisemessage',
            name='buyer_msg_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='promisemessage',
            name='seller_msg_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
    ]
