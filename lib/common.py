#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.conf import settings
from django.utils import timezone
from socket import socket,AF_INET, SOCK_STREAM
import json, subprocess
import redis, time



def return_json_data(data):
    if isinstance(data["status"], dict) and "status" in data.keys() and isinstance(data["status"], int):
       return HttpResponse(status=data["status"], content_type='application/text', charset='utf-8',data=data["msg"])
    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type='application/json', charset='utf-8')

def check_login(func):
    """登录验证"""
    def _request_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/openvpn/login/")

    return _request_view

def check_secret_key(func):
    """api 密钥验证"""
    def _request_view(request, *args, **kwargs):
        if request.method == 'POST':
            data = request.body
            if not data:
                return return_json_data({"status": "error", "msg": "没有数据"})
            try:
                json_data = json.loads(data)
            except:
                return return_json_data({"status": "error", "msg": "json解析失败"})
            if "SECRET_KEY" not in json_data.keys() or json_data["SECRET_KEY"] != settings.SECRET_KEY:
                return return_json_data({"status": "error", "msg": "api 接口认证失败"})
            return func(request, *args, **kwargs)
        else:
            return return_json_data({"status": "error", "msg": "请求方法错误"})

    return _request_view

def key_parameter(key_data,rest_data):
    """检测字典中是否有指定关键字"""
    def key_is(key_str,rest_data):
        if key_str not in rest_data.keys():
            return {"rest": False, "msg": "检测对象不存在关键字"}
        return {"rest": True, "msg": ""}

    if not isinstance(rest_data, dict):
        return {"rest": False,"msg": "检测对象必须为字典格式"}

    if isinstance(key_data, str):
        return key_is(key_data,rest_data)

    elif isinstance(key_data, list):
        for key in key_data:
            if key not in "" and key not in None:
                return {"rest": False, "msg": "关键子列表中有为空项"}
            tmp_data = key_is(key, rest_data)
            if not tmp_data["rest"]:
                return tmp_data
        return {"rest": True, "msg": ""}

    else:
        return {"rest": False, "msg": "不支持关键字类型，目前只支持 字符串和列表"}


class Cmd(object):
    """本地执行"""
    def onetime_shell(self, cmd) -> object:
        cmd = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        cmd = cmd.communicate()
        cmd = cmd[0].decode().rstrip()
        return cmd

# class Remote_cmd(object):
#     """远程执行"""
#
#     def __init__(self, IP, Port, User, Password):
#         self.ssh = paramiko.SSHClient()
#         self.set_missing_host_key_policy = self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         self.connect = self.ssh.connect(hostname=IP, port=Port, username=User, password=Password, timeout=10)
#
#     def onetime_shell(self, cmd, notice=False):
#         stdin, stdout, stderr = self.ssh.exec_command(cmd)
#         result = stdout.read().decode('utf-8').rstrip()
#         if notice:
#            self.ssh.close()
#         return result


class tcp_socker(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.rece_bytes_global = {}
        self.sent_bytes_global = {}
        self.vpn_socket = self.socket_init()


    def socket_init(self):
        vpn_conn = socket(AF_INET, SOCK_STREAM)
        vpn_conn.connect((self.host, self.port))
        vpn_conn.recv(2048)
        return vpn_conn

    def close(self):
        self.vpn_socket.send("exit\n".encode("utf-8"))
        self.vpn_socket.close()

def format_time(_datatime):
    if _datatime:
        return timezone.get_current_timezone().localize(_datatime)
    return _datatime


class redis_get(object):
    '''redis模块'''
    def __init__(self,host_ip,host_port,dbname=0,passwd=None):
        Pool = redis.ConnectionPool(host=host_ip, port=host_port, db=dbname, max_connections=5)
        self.redir_conn = redis.Redis(connection_pool=Pool)

    def GetListData(self,list_key,start_data,end_data):
        redis_data = self.redir_conn.lrange(list_key,start_data,end_data)
        return redis_data

    def GetListLen(self,list_key):
        redis_key_len = self.redir_conn.llen(list_key)
        return redis_key_len

    def DelListData(self,list_key,start_data,ent_data=-1):
        return self.redir_conn.ltrim(list_key,start_data,ent_data)

    def redis_set(self,KEY,DATA):
        return self.redir_conn.set(KEY,DATA)

    def redis_get(self,KEY):
        return self.redir_conn.get(KEY)


def fromt_time(timeStamp):
    timeArray = time.localtime(timeStamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", timeArray)



