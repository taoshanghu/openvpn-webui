# Generated by Django 2.2.24 on 2023-05-26 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openvpn', '0008_auto_20220216_1452'),
    ]

    operations = [
        migrations.AddField(
            model_name='openvpn_online_user',
            name='login_type',
            field=models.BooleanField(default='0', verbose_name='验证状态(1认证成功|0认证失败)'),
        ),
    ]
