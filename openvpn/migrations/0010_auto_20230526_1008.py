# Generated by Django 2.2.24 on 2023-05-26 02:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openvpn', '0009_openvpn_online_user_login_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openvpn_online_user',
            name='login_type',
            field=models.BooleanField(default=False, verbose_name='验证状态(1认证成功|0认证失败)'),
        ),
    ]
