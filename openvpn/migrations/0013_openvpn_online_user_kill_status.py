# Generated by Django 2.2.24 on 2023-06-13 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openvpn', '0010_auto_20230526_1008'),
    ]

    operations = [
        migrations.AddField(
            model_name='openvpn_online_user',
            name='kill_status',
            field=models.BooleanField(default=False, verbose_name='是否强制下线(1强制|0不强制)'),
        ),
    ]
