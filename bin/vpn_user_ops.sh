#!/bin/bash
##Date:         2022-01-18
##Author:       taoshanghu
##Version:      1.0

api_base_connect="http://127.0.0.1:8080/openvpn/user_connect"
api_base_disconnect="http://127.0.0.1:8080/openvpn/user_disconnect"
vpn_user_login="http://127.0.0.1:8080/openvpn/vpn_user_login"
SECRET_KEY='!b#ulek-d*r-kec5ny(fn*r=88h9cf5xr#e+9^k2!(!gq$gvx1' #django settings
time_data=$(date "+%Y-%m-%d %H:%M:%S")

#用户上线
connect() {
  json_data='{"username":"'$username'","remove_add":"'$trusted_ip'","virtual_add":"'$ifconfig_pool_remote_ip'","BTime":"'$time_data'","SECRET_KEY":"'$SECRET_KEY'"}'
  http_rest=$(curl -i -X POST -H "'Content-type':'application/json'" -d "$json_data" $api_base_connect)
}

#用户下线
disconnect() {
  json_data='{"username":"'$username'","BTime":"'$time_data'","SECRET_KEY":"'$SECRET_KEY'"}'
  http_rest=$(curl -i -X POST -H "'Content-type':'application/json'" -d "$json_data" $api_base_disconnect)
}

check_user() {
  json_data='{"username":"'$username'","password":"'$time_data'","SECRET_KEY":"'$SECRET_KEY'"}'
  http_rest=$(curl -i -X POST -H "'Content-type':'application/json'" -d "$json_data" $vpn_user_login)
  if [ $http_rest == "ok" ]; then
    exit 0
  else
    exit 1
  fi
}

case $1 in
  connect)
    connect
    exit 0
    ;;
  disconnect)
    disconnect
    exit 0
    ;;
  check_user)
    check_user
    exit 0
    ;;
  *)
    echo "connect|disconnect"
    exit 1
esac




