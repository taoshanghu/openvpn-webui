from lib.common import return_json_data
from openvpn.models import openvpn_sun_flow, openvpn_online_user, openvpn_flow
from django.contrib.auth.models import User
from django.conf import settings
from lib.common import Cmd
from django.db.models import Q
import os

def is_user_superuser(username):
    if not username:
        return return_json_data({"status": "error", "msg": "未获取到登录账户"})
    user_info = User.objects.filter(username=username).values("username", "is_superuser")
    if len(user_info) < 1:
        return return_json_data({"status": "error", "msg": "登录用户不存在"})
    if user_info[0]["is_superuser"]:
        return True
    else:
        return False

def update_passwd(username,password):
    USER = User.objects.get(username=username)
    USER.set_password(password)
    USER.save()
    return {"status": "success", "msg": "密码修改成功"}

def vpn_flow_select(username,start_time,end_date):
    if username in "all":
        vpn_flow = openvpn_flow.objects.filter(
            flow_time__range=[end_date,start_time]
        ).values(
            "username", "sent_flow", "rece_flow", "flow_time"
        )
    else:
        vpn_flow = openvpn_flow.objects.filter(
            flow_time__range=[end_date,start_time]
        ).values(
            "sent_flow", "rece_flow", "flow_time"
        )
    print("vpn_flow",vpn_flow)
    return vpn_flow

def online_user_select(username):
    if username in "all":
        user_data = openvpn_online_user.objects.filter(
            vpn_login=True
        ).values(
            "username", "client_ID", "remove_add", "virtual_add", "time_online"
        )
    else:
        user_data = openvpn_online_user.objects.filter(
            username=username, vpn_login=True
        ).values(
            "username", "client_ID", "remove_add", "virtual_add", "time_online"
        )
    return user_data

def user_login_select(all=None,std=None,sed=None):
    if all:
        user_data = openvpn_online_user.objects.filter(
            vpn_login=True
        ).values(
            "username",
            "remove_add",
            "virtual_add",
            "time_online",
            "offline_time",
            "login_type"
        )
    else:
        user_data = openvpn_online_user.objects.filter(
            Q(time_online__gt=std) & Q(time_online__lt=sed)
            #time_online__range = [std,sed]
        ).values(
            "username",
            "remove_add",
            "virtual_add",
            "time_online",
            "offline_time",
            "login_type"
        )
    return user_data

def create_vpn_user(username):
    shell = Cmd()
    add_user_cmd = "%s/open_user.sh add_user %s %s" % (settings.SHELL_PATH, username, settings.VPN_CONF_PATH)
    print(shell.onetime_shell(add_user_cmd))
    open_config_file = "%s/%s.ovpn" % (settings.VPN_CONF_PATH, username)
    if not os.path.exists(open_config_file):
        return open_config_file
    else:
        return None

def del_vpn_user(username):
    shell = Cmd()
    add_user_cmd = "%s/open_user.sh del_user %s" % (settings.SHELL_PATH, username)
    print(shell.onetime_shell(add_user_cmd))
    open_config_file = "%s/%s.ovpn" % (settings.VPN_CONF_PATH, username)
    if not os.path.exists(open_config_file):
        os.remove(open_config_file)
