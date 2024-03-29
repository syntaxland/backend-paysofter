# Generated by Django 3.2.20 on 2024-02-18 18:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('promise', '0030_auto_20240215_1714'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promisemessage',
            name='buyer_msg_count',
        ),
        migrations.RemoveField(
            model_name='promisemessage',
            name='seller_msg_count',
        ),
        migrations.AddField(
            model_name='paysofterpromise',
            name='buyer_msg_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='paysofterpromise',
            name='seller_msg_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='promisemessage',
            name='buyer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='promise_message_buyer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='promisemessage',
            name='seller',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='promise_message_seller', to=settings.AUTH_USER_MODEL),
        ),
    ]
