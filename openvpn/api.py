from lib.common import return_json_data, check_secret_key
from django.http import HttpResponse
from django.contrib.auth import authenticate
from openvpn.models import openvpn_online_user,openvpn_flow,openvpn_sun_flow
from django.db.models import Q
import json, time
from lib.common import fromt_time


@check_secret_key
def vpn_user_disconnect(request):
    if request.method == 'POST':
        data = request.body
        json_data = json.loads(data)
        openvpn_online_user.objects.filter(
            username=json_data["username"],vpn_login=True
            ).update(
            offline_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),vpn_login=False
        )
        return HttpResponse("ok",content_type='application/text',charset='utf-8')

    else:
        return HttpResponse("no",content_type='application/text',charset='utf-8')

@check_secret_key
def vpn_user_connect(request):
    if request.method == 'POST':
        data = request.body
        json_data = json.loads(data)
        if json_data["Client_id"]:
            Client_id = json_data["Client_id"]
        else:
            Client_id = "kong"
        openvpn_online_user.objects.create(username=json_data["username"],
                                           client_ID=Client_id,
                                           vpn_login=True,
                                           remove_add=json_data["remove_add"],
                                           virtual_add=json_data["virtual_add"],
                                           time_online=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                           offline_time="",
                                           desc="")
        return HttpResponse("ok",content_type='application/text',charset='utf-8')

    else:
        return HttpResponse("no",content_type='application/text',charset='utf-8')

@check_secret_key
def vpn_conn_user_auth(request):
    if request.method == 'POST':
        data = request.body
        json_data = json.loads(data)
        user_auth = authenticate(username=json_data["username"], password=json_data["password"])
        if user_auth is not None:
            return HttpResponse("ok",content_type='application/text',charset='utf-8')
        else:
            return HttpResponse("no",content_type='application/text',charset='utf-8')
    else:
        return HttpResponse("no",content_type='application/text',charset='utf-8')

@check_secret_key
def save_openvpn_status(request):
    """保存openvpn status 数据"""
    if request.method == 'POST':
        data = json.loads(request.body)
        openvpn_flow_obj = []
        local_Time = time.strftime("%Y-%m-%d %H:%M:%S")
        for client in data["data"]:
            openvpn_online_user.objects.filter(username=client["username"], vpn_login=True).update(
                client_ID=client["client_id"]
            )
            obj = openvpn_flow(username=client["username"], sent_flow=client["sent_flow"],
                               rece_flow=client["rece_flow"],
                               flow_time=str(local_Time), desc=""
                               )
            openvpn_flow_obj.append(obj)
        openvpn_flow.objects.bulk_create(openvpn_flow_obj)

        #"""OPENVPN 总流量 保存数据库"""
        # openvpn_sun_flow.objects.create(sent_flow=data["sun_flow"]["sun_set_flow"], rece_flow=data["sun_flow"]["sun_rece_flow"],flow_time=data["time"])
        return return_json_data({"status":"success"})
    else:
        return return_json_data({"status": "error", "msg": "方法错误"})


#@check_secret_key
def kill_client(request):
    timeStamp = int(time.time())
    start_time = fromt_time(timeStamp)
    end_date = fromt_time(timeStamp - 43200)
    client_kill_id = openvpn_online_user.objects.filter(Q(vpn_login=1, kill_status=1) & Q(time_online__range=[end_date,start_time])).values("username")
    k_c_id = []
    k_c_name = []
    print(client_kill_id)
    for client_id in client_kill_id:
        k_c_id.append(client_id["username"])
    openvpn_online_user.objects.filter(vpn_login=1, username__in=k_c_id).update(kill_status=0)
    if k_c_name:
        client_kill = k_c_id
    else:
        client_kill = []
    return return_json_data({"status": "success", "msg": client_kill})
