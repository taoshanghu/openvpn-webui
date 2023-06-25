import json
import os.path
from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from lib.common import return_json_data,check_login
from django.views.decorators.clickjacking import xframe_options_exempt
from openvpn.models import openvpn_online_user
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from openvpn.lib import create_vpn_user
from django.conf import settings
from django.http import FileResponse
from openvpn.lib import is_user_superuser,update_passwd,vpn_flow_select,online_user_select, user_login_select
import time
import datetime



@xframe_options_exempt
@check_login
def cruate_user(request):
    if request.method == 'POST':
        username = request.POST.get("Username", None)
        password = request.POST.get("Password", None)
        user_role = request.POST.get("user_role", None)
        first_name = request.POST.get("first_name", None)
        if not username or not password:
            return return_json_data({"status":"error", "msg": "用户名或密码 空"})

        #判断操作用户 角色
        user_superuser = is_user_superuser(request.session.get("username"))
        if not user_superuser:
            return return_json_data({"status": "success", "msg": "权限错误"})

        is_user = User.objects.filter(username=username).values("username")
        if len(is_user) == 0:
            if user_role:
                User.objects.create_superuser(username=username, password=password,first_name=first_name, is_active=True)
            else:
                User.objects.create_user(username=username, password=password, first_name=first_name,is_active=True)
            open_config_file = create_vpn_user(username)
            if open_config_file:
                return return_json_data({"status": "success", "msg": "创建完成"})
            else:
                return return_json_data({"status": "error", "msg": "创建配置文件失败"})

        else:
            return return_json_data({"status":"error", "msg": "用户已存在"})
    return return_json_data({"status":"error", "msg": "请求方法错误"})

@check_login
def delete_user(request):
    if request.method == 'POST':
        # 判断操作用户 角色
        user_superuser = is_user_superuser(request.session.get("username",""))
        if not user_superuser:
            return return_json_data({"status": "success", "msg": "权限错误"})
        del_username = json.loads(request.body)
        if not del_username:
            return return_json_data({"status": "success", "msg": "用户名为空"})
        delete_result = User.objects.filter(username=del_username["user_name"]).delete()
        #del_vpn_user(request.session.get("username"))
        if delete_result:
            return return_json_data({"status": "success", "msg": "删除用户 %s 成功" % del_username["user_name"]})
        else:
            return return_json_data({"status": "success", "msg": "用户 %s 未注册" % del_username["user_name"]})

@check_login
def update_user_pass(request):
    login_data = {"login_data": u"用户名或密码为空"}
    if request.method == 'POST':
        username = request.POST.get("username", None)
        load_password = request.POST.get("load_password", None)
        new_password = request.POST.get("new_password", None)

        if not username or not new_password:
            login_data["login_data"] = u"用户名或密码为空"
            return return_json_data({"status": "error", "msg": "未获取到更新密码 用户名或密码"})


        user_info = User.objects.filter(username=username)
        if len(user_info) < 1:
            return return_json_data({"status": "error", "msg": "用户不存在"})
        # 判断操作用户 角色
        user_superuser = is_user_superuser(request.session.get("username"))
        if user_superuser:
            return return_json_data(update_passwd(username,new_password))

        if request.session.get("username") != username:
            return return_json_data({"status": "error", "msg": "权限不足"})
        user_auth = authenticate(username=username, password=load_password)

        if user_auth:
            return return_json_data(update_passwd(username,new_password))
        else:
            return return_json_data({"status": "error", "msg": "原密码不正确"})
    return return_json_data({"status":"error", "msg": "请求方法错误"})

@check_login
def openvpn_flow_views(request):
    "查询vpn流量"
    if request.method == 'GET':
        user_info = is_user_superuser(request.session.get("username"))
        openvpn_time_duration = 30 #分钟24 * 60 1640
        start_date = timezone.datetime.now()
        end_date = start_date - timezone.timedelta(minutes=openvpn_time_duration)
        data = []
        if user_info:
            vpn_flow = vpn_flow_select(username="all", start_time=start_date,end_date=end_date)
        else:
            vpn_flow = vpn_flow_select(username=request.session.get("username"), start_time=start_date, end_date=end_date)
        print("flow",vpn_flow)
        if len(vpn_flow) > 0:
            for flow in vpn_flow:
                data.append({
                    "username": flow["username"],
                    "sent_flow": flow["sent_flow"],
                    "rece_flow": flow["rece_flow"],
                    "flow_time": flow["flow_time"]
                })
        return return_json_data({"status":"success", "msg": data})

@check_login
def get_online_user(request):
    """查看在线用户信息"""
    if request.method == 'GET':
        user_info = is_user_superuser(username=request.session.get("username"))
        if user_info:
            user_data = online_user_select(username="all")
        else:
            user_data = online_user_select(username=request.session.get("username"))

        data2 = []
        for user in user_data:
            data2.append({
                "vpn_name":user["username"],
                "client_ID": user["client_ID"],
                "remove_addr": user["remove_add"],
                "virtual_addr": user["virtual_add"],
                "online_time" : str(user["time_online"]),
                "sent_bytes" : "5000",
                "rece_bytes": "6000",
                "nlin": "cn",
                "city": "上海",
            })
        return return_json_data({"status":"success", "msg": data2})

@check_login
def get_all_user(request):
    """账户管理"""
    if request.method == 'GET':
        user_info_list = User.objects.filter(username=request.session.get("username"))
        if len(user_info_list) > 0:
            user_info = user_info_list[0]
        else:
            return return_json_data({"status": "error", "msg": "用户不存在"})
        user_data_info = User.objects.filter().values("username", "first_name")
        user_data = []
        if user_info.is_superuser:

            for user in user_data_info:

                user_data_tmp = openvpn_online_user.objects.filter(
                    username=user["username"]
                ).values(
                    "username",
                    "client_ID",
                    "remove_add",
                    "virtual_add",
                    "time_online"
                )[:0]

                if len(user_data_tmp) > 0:
                    user_data.append(user_data_tmp)
                else:
                    print(user)
                    user_data.append({
                        "username": user["username"],
                        "first_name": user["first_name"],
                        "client_ID": "kong",
                        "remove_add": "kong",
                        "virtual_add": "kong",
                        "time_online": "kong"
                    })

        else:
            username = request.session.get("username")
            user_data_info = User.objects.filter(username=username).values( "first_name")
            if user_data_info[0]["first_name"]:
                first_name = user_data_info[0]["first_name"]
            else:
                first_name = "None"
            print(user_data_info)
            user_data_tmp = openvpn_online_user.objects.filter(
                username=username
            ).values(
                "username",
                "client_ID",
                "remove_add",
                "virtual_add",
                "time_online"
            )[:0]

            if len(user_data_tmp) > 0:
                user_data.append(user_data_tmp)
            else:
                user_data.append({
                    "username": username,
                    "first_name": first_name,
                    "remove_add": "None",
                    "virtual_add": "None",
                    "time_online": "None"
                })

        data2 = []
        for user in user_data:
            print(user)
            data2.append({
                "vpn_name":user["username"],
                "first_name": user["first_name"],
                "client_ID": user["client_ID"],
                "remove_addr": user["remove_add"],
                "virtual_addr": user["virtual_add"],
                "online_time" : str(user["time_online"]),
                "sent_bytes" : "5000",
                "rece_bytes": "6000",
                "nlin": "cn",
                "city": "上海",
                "vpn_config": "/%s/%s.ovpn" % (settings.VPN_CONF_PATH_NAME, user["username"])
            })
        return return_json_data({"status": "success", "msg": data2})

@check_login
def index(request):
    return render(request, "index.html")

@check_login
def user_html(request):
    """user html"""
    user_info_list = User.objects.filter(username=request.session.get("username"))
    if len(user_info_list) > 0:
        user_info = user_info_list[0]
    else:
        return return_json_data({"status": "error", "msg": "用户不存在"})
    login_data = {"user_admin": 0}

    if user_info.is_superuser:
        login_data["user_admin"] = 1
        return render(request, "user.html",login_data)
    else:
        return render(request, "user.html", login_data)

def user_login(request):
    """用户登录"""
    login_data = {"login_data": u"用户名或密码为空"}
    if request.method == 'POST':
        username = request.POST.get("Username",None)
        password = request.POST.get("Password",None)

        if not username or not password:
            login_data["login_data"] = u"用户名或密码为空"
            return render(request, "login.html", login_data)

        user_auth = authenticate(username=username, password=password)
        if user_auth is None:
            login_data["login_data"] = u"用户名或密码验证失败"
            return render(request, "login.html", login_data)
        else:
            request.session['username'] = username
            login(request,user_auth)
            return HttpResponseRedirect("/openvpn/index")
    return render(request, "login.html", login_data)

@check_login
def user_logout(request):
    """用户退出"""
    login_data = {"login_data": u"用户名或密码为空"}
    logout(request)
    return render(request, "login.html", login_data)

@check_login
def user_logout(request):
    """用户退出"""
    login_data = {"login_data": u"欢迎光临"}
    logout(request)
    return render(request, "login.html", login_data)

@check_login
def config_down(request):
    config_name = "%s.ovpn" % (request.GET.get("username", None))
    config_path = "%s/%s" % (settings.VPN_CONF_PATH, config_name)
    if not os.path.isfile(config_path):
        return return_json_data({"status": "error", "msg": "未找到配置文件"})
    file_name = open(config_path, 'r')
    response = FileResponse(file_name)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="%s"' % config_name
    return HttpResponse(file_name)

@check_login
def user_monitoring(request):
    if request.method == 'GET':
        user_superuser = is_user_superuser(request.session.get("username"))
        if not user_superuser:
            return return_json_data({"status": "success", "msg": {"sum_user":0, "Online_users":0}})
        sum_user = User.objects.aggregate(Count = Count("username", distinct=True))
        Online_users = openvpn_online_user.objects.filter(vpn_login=True)
        return return_json_data({"status": "success", "msg": {"sum_user": sum_user["Count"], "Online_users": len(Online_users)}})
    return return_json_data(
        {"status": "error", "msg": "请求方法错误"})

@check_login
def kill_user(request):
    """断开在线VPN通道"""
    if request.method == 'POST':
        user_info = is_user_superuser(username=request.session.get("username"))
        if not user_info:
            return return_json_data({"status":"error", "msg": "没有权限"})
        print(request.body)
        kill_username = json.loads(request.body)
        openvpn_online_user.objects.filter(vpn_login=1, username=kill_username["username"]).update(kill_status=1)
        return return_json_data({"status": "success", "msg": "用户断开成功"})
    return return_json_data({"status": "error", "msg": "请求方法错误"})

@check_login
def user_active(request):
    """禁止用户登录"""
    if request.method == 'POST':
        user_info = is_user_superuser(username=request.session.get("username"))
        if not user_info:
            return return_json_data({"status":"error", "msg": "没有权限"})
        print(request.body)
        kill_username = json.loads(request.body)
        if not is_user_superuser(username=kill_username["username"]):
            User.objects.filter(username=kill_username["username"]).update(is_active=False)
            return return_json_data({"status": "success", "msg": "禁止登录成功"})
        else:
            return return_json_data({"status": "error", "msg": "管理员账户不能禁止登录"})
    else:
        return return_json_data({"status": "error", "msg": "请求方法错误"})

@check_login
def get_user_login_log_data(request):
    """查看日志信息"""
    if request.method == 'GET':
        log_data_type = request.GET.get("log_data_type","")
        time_std = request.GET.get("time_std","")
        time_sed = request.GET.get("time_sed", "")
        if log_data_type:
            user_data = user_login_select(all=log_data_type)
        elif time_std and time_sed:
            time_std = "%s 00:00:00" % time_std
            time_sed = "%s 00:00:00" % time_sed
            user_data = user_login_select(sed=time_sed,std=time_std)
        else:
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            time_std_obj = datetime.datetime.now()
            time_sed_obj = (time_std_obj - datetime.timedelta(days=7))
            time_std = "%s 00:00:00" % str(time_std_obj.strftime("%Y-%m-%d"))
            time_sed = "%s 00:00:00" % str(time_sed_obj.strftime("%Y-%m-%d"))
            user_data = user_login_select(sed=time_sed,std=time_std)

        data2 = []
        for user in user_data:
            data2.append({
                "vpn_name":user["username"],
                "remove_addr": user["remove_add"],
                "virtual_addr": user["virtual_add"],
                "online_time" : str(user["time_online"]),
                "offline_time": str(user["offline_time"]),
                "login_type" : str(user["login_type"]),
            })
        return return_json_data({"status":"success", "msg": data2})

@check_login
def get_user_login_log(request):
    return render(request, "vpn_login_log.html")


