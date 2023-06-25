from django.db import models
from django.contrib.auth.models import User

class openvpn_online_user(models.Model):
    """openvpn 客户端连接日志"""
    "vpn_login 1 登录  0 未登录"
    username = models.CharField(verbose_name=u"VPN账户",max_length=30)
    vpn_login = models.BooleanField(verbose_name=u"VPN登录标记",default=False)
    login_type = models.BooleanField(verbose_name=u"验证状态(1认证成功|0认证失败)", default=False)
    client_ID = models.CharField(verbose_name=u"客户端ID",max_length=10)
    remove_add = models.CharField(verbose_name=u"客户端外网地址",max_length=22)
    virtual_add = models.CharField(verbose_name=u"VPN分配地址",max_length=15)
    kill_status = models.BooleanField(verbose_name=u"是否强制下线(1强制|0不强制)", default=False)
    time_online = models.CharField(verbose_name=u"上线时间",null=False,max_length=300)
    offline_time = models.CharField(verbose_name=u'下线时间',null=True,max_length=300)
    desc = models.CharField(u"备注", max_length=300, blank=True,default=None)

    def __str__(self):
        return self.username

class openvpn_flow(models.Model):
    """openvpn 客户端流量"""
    username = models.CharField(verbose_name=u"VPN账户",max_length=30)
    sent_flow = models.BigIntegerField(verbose_name=u"上行流量")
    rece_flow = models.BigIntegerField(verbose_name=u"下线流量")
    flow_time = models.CharField(verbose_name=u"传输时间",max_length=300)
    desc = models.CharField(u"描述", max_length=300, blank=True,default=None)

    def __str__(self):
        return self.flow_time

class openvpn_sun_flow(models.Model):
    """openvpn 总流量"""
    sent_flow = models.BigIntegerField(verbose_name=u"上行流量")
    rece_flow = models.BigIntegerField(verbose_name=u"下线流量")
    flow_time = models.CharField(verbose_name=u"传输时间",max_length=300)

    def __str__(self):
        return self.flow_time
