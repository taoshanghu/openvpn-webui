# Generated by Django 2.2.24 on 2022-02-16 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openvpn', '0006_auto_20220122_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openvpn_flow',
            name='rece_flow',
            field=models.BigIntegerField(verbose_name='下线流量'),
        ),
        migrations.AlterField(
            model_name='openvpn_flow',
            name='sent_flow',
            field=models.BigIntegerField(verbose_name='上行流量'),
        ),
        migrations.AlterField(
            model_name='openvpn_flow',
            name='username',
            field=models.CharField(max_length=30, verbose_name='VPN账户'),
        ),
        migrations.AlterField(
            model_name='openvpn_online_user',
            name='remove_add',
            field=models.CharField(max_length=22, verbose_name='客户端外网地址'),
        ),
        migrations.AlterField(
            model_name='openvpn_sun_flow',
            name='rece_flow',
            field=models.BigIntegerField(verbose_name='下线流量'),
        ),
        migrations.AlterField(
            model_name='openvpn_sun_flow',
            name='sent_flow',
            field=models.BigIntegerField(verbose_name='上行流量'),
        ),
    ]
