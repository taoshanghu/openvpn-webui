# Generated by Django 2.2.24 on 2022-01-22 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openvpn', '0005_openvpn_online_user_vpn_login'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openvpn_flow',
            name='flow_time',
            field=models.DateTimeField(max_length=300, verbose_name='传输时间'),
        ),
        migrations.AlterField(
            model_name='openvpn_online_user',
            name='offline_time',
            field=models.CharField(max_length=300, null=True, verbose_name='下线时间'),
        ),
        migrations.AlterField(
            model_name='openvpn_online_user',
            name='time_online',
            field=models.CharField(max_length=300, verbose_name='上线时间'),
        ),
        migrations.AlterField(
            model_name='openvpn_sun_flow',
            name='flow_time',
            field=models.CharField(max_length=300, verbose_name='传输时间'),
        ),
    ]
