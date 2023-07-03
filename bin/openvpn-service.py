#!/bin/python3

import socket, requests, json
import time, os, sys, signal
from multiprocessing import Process, Value

'''初始化全局方法'''
proc_status = Value('b',False)
proc_status2 = Value('i',0)
Process_list = 1


OPEMVPN_HOST = "127.0.0.1"
OPEMVPN_PORT = 44490
SECRET_KEY = "!b#ulek-d*r-kec5ny(fn*r=88h9cf5xr#e+9^k2!(!gq$gvx1"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
tmp_flow_file = "%s/tmp_flow.tmp" % BASE_DIR
tmp_flow = {}

def log(log_data):
    logfile = "%s/openvon_server.log" % BASE_DIR
    LogTime = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(logfile, "a+", encoding='utf-8') as f:
        f.write("%s %s\n" % (LogTime, log_data))

class open_vpn(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.__openvpn_tcp_socket()

    def status(self):
        cmd = "status"
        data = self.__send(cmd)
        return data

    def get_client_id(self):
        openvpn_status = self.status()
        client_data = []
        for client in openvpn_status.split("\n"):
            if "HEADER,CLIENT_LIST" in client:
                continue
            if "CLIENT_LIST" in client:
                 client_data.append(self.client_jx(client))
        return client_data


    def kill_client(self,client_id):
        data = self.get_client_id()
        for id in client_id:
            for cl in data:
                if cl["username"] == id:
                    cmd = "client-kill %s" % cl["client_id"]
                    self.__send(cmd)

    def help(self):
        cmd = "help"
        print(self.__send(cmd))

    def version(self):
        cmd = "version"
        v_data = self.__send(cmd)
        for I in v_data.split("\n"):
            if "OpenVPN Version" in I:
                openvpn_version = I.split(" ")[3]
                openvpn_version_list = openvpn_version.split(".")
                if int(openvpn_version_list[0]) != 2:
                    raise Exception("openvpn-server 版本要求2.4.* 当前运行版本 %s" % openvpn_version)
                if int(openvpn_version_list[1]) != 4:
                    raise Exception("openvpn-server 版本不匹配")
                return

    def close(self):
        cmd = "exit"
        self.__send(cmd)
        self.VPN_SOCK.close()

    def __openvpn_tcp_socket(self):
        self.VPN_SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.VPN_SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 5)
        self.VPN_SOCK.connect((OPEMVPN_HOST, OPEMVPN_PORT))

    def __send(self, cmd):
        tmp_cmd = "%s\r\n" % cmd
        print(tmp_cmd)
        self.VPN_SOCK.send(tmp_cmd.encode() )
        rest_data, lock_shu = "", 0
        while lock_shu < 20:
            lock_shu += 1
            data = self.VPN_SOCK.recv(2048)
            tmp_data = data.decode()
            rest_data = rest_data + tmp_data
            if tmp_data.endswith("END\r\n"):
                return rest_data

    def client_jx(self, openvpn_client_data):
        global tmp_flow
        list_client_data = openvpn_client_data.split(",")
        data = {
            "username": list_client_data[1],
            "remove_add": list_client_data[2],
            "virtual_addr": list_client_data[3],
            "client_id": list_client_data[10]
        }
        new_rece_flow = int(int(list_client_data[5]) / 1000)
        new_sent_flow = int(int(list_client_data[6]) / 1000)
        if data["username"] in tmp_flow.keys():
            if new_rece_flow >= tmp_flow[data["username"]]["rece_flow"] and new_sent_flow >= tmp_flow[data["username"]]["sent_flow"]:
                data["rece_flow"] = new_rece_flow - tmp_flow[data["username"]]["rece_flow"]
                data["sent_flow"] = new_sent_flow - tmp_flow[data["username"]]["sent_flow"]
                tmp_flow[data["username"]]["rece_flow"] = new_rece_flow
                tmp_flow[data["username"]]["sent_flow"] = new_sent_flow
            else:
                data["rece_flow"] = new_rece_flow
                data["sent_flow"] = new_sent_flow
                tmp_flow[data["username"]]["rece_flow"] = new_rece_flow
                tmp_flow[data["username"]]["sent_flow"] = new_sent_flow
        else:
            tmp_flow[data["username"]] = {"rece_flow": new_rece_flow, "sent_flow": new_sent_flow}
        return data

class openvpn_web(object):
    def __init__(self, host="127.0.0.1:8080"):
        self.host = host
        self.headers =  {'Content-Type': 'application/json'}

    def flow_send(self,data):
        openvpn_web_url = "http://%s/openvpn/save_openvpn_status" % self.host
        self.http(url=openvpn_web_url, data=data)

    def kill_client(self):
        openvpn_web_url = "http://%s/openvpn/kill_client/" % self.host
        kill_client = self.http(url=openvpn_web_url)
        return kill_client["msg"]

    def http(self, url, data=None):
        if data:
            post_data = {"SECRET_KEY": SECRET_KEY, "data": data}
            try:
                response = requests.post(url=url, data=json.dumps(post_data), headers=self.headers)
            except requests.exceptions.ConnectionError as err:
                print(err)
                return
            if response.status_code != 200:
                log("推送数据失败 推送URL:%s  推送数据: %s" % (url, data))
        else:
            try:
                response = requests.get(url=url)
            except requests.exceptions.ConnectionError as err:
                log(err)
                return
            if response.status_code != 200:
                log("推送数据失败 推送URL:%s  推送数据: %s" % (url, data))
            else:
                return response.json()

def set_client(obj_ovpn, ojb_web, proc_id):
    global tmp_flow
    if os.path.isfile(tmp_flow_file):
        with open(tmp_flow_file, "r", encoding="utf-8") as f:
            tmp_flow_data = f.read()
            tmp_flow = json.loads(tmp_flow_data)
    i = 0
    while proc_status.value:
        if i < 30:
            i += 1
            time.sleep(1)
            continue
        client_data = obj_ovpn.get_client_id()
        if isinstance(client_data, list) and len(client_data) > 0:
            ojb_web.flow_send(client_data)
        with open(tmp_flow_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(tmp_flow))
        i = 0
    else:
        proc_status2.value = proc_status2.value + 1
        print(u"业务进程：%s  停止成功" % proc_id)


def get_kill(obj_ovpn, ojb_web, proc_id):
    while proc_status.value:
        kill_client_id = ojb_web.kill_client()
        if isinstance(kill_client_id, list) and len(kill_client_id) > 0:
            obj_ovpn.kill_client(kill_client_id)
        time.sleep(1)
    else:
        proc_status2.value = proc_status2.value + 1
        print(u"业务进程：%s  停止成功" % proc_id)



def proc_stop(signum, frame):
    print("proc_status_stop",proc_status.value)
    proc_status.value = False
    i = 0
    while i < 5:
        if proc_status2.value == Process_list:
            print("服务停止成功")
            sys.exit(0)
        else:
            time.sleep(1)
            i += 1
    else:
        print("服务停止成功")
        sys.exit(0)

def main():
    """主进程 负责创建工作进程和维护工作进程"""
    ovpn = open_vpn(OPEMVPN_HOST,OPEMVPN_PORT)
    http_m = openvpn_web()
    ovpn.version()

    print("主服务启动成功")
    proc_status.value = True
    p_name1 =  "flow_collection"
    p_name2 = "kill_client"
    prc1, prc2= None, None


    #工作进程监控
    while proc_status.value:
        time.sleep(1)
        if not prc1 or not prc1.is_alive():
            prc1 = Process(target=set_client, args=(ovpn, http_m, p_name1))
            prc1.start()
        if not prc2 or not prc2.is_alive():
            prc2 = Process(target=get_kill, args=(ovpn, http_m,p_name2))
            prc2.start()




if __name__ == "__main__":
    signal.signal(signal.SIGINT, proc_stop)
    signal.signal(signal.SIGHUP, proc_stop)
    signal.signal(signal.SIGTERM, proc_stop)
    main()