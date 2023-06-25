#!/bin/bash
##Date:         2022-01-18
##Author:       taoshanghu
##Version:      1.0

api_bash_host="127.0.0.1:8080"
api_base_connect="http://$api_bash_host/openvpn/user_connect"
api_base_disconnect="http://$api_bash_host/openvpn/user_disconnect"
vpn_user_login="http://$api_bash_host/openvpn/vpn_user_login"
SECRET_KEY='!b#ulek-d*r-kec5ny(fn*r=88h9cf5xr#e+9^k2!(!gq$gvx1' #django settings
time_data=$(date "+%Y-%m-%d %H:%M:%S")

#用户上线
connect() {
  json_data='{"username":"'$username'","remove_add":"'$trusted_ip'","virtual_add":"'$ifconfig_pool_remote_ip'","Client_ID": "'$Client_ID'","SECRET_KEY":"'$SECRET_KEY'"}'
  http_rest=$(curl -s -m 10 -X POST -H "'Content-type':'application/json'" -d "$json_data" $api_base_connect)
}

#用户下线
disconnect() {
  json_data='{"username":"'$username'","SECRET_KEY":"'$SECRET_KEY'"}'
  http_rest=$(curl -s -m 10 -X POST -H "'Content-type':'application/json'" -d "$json_data" $api_base_disconnect)
}

check_user() {
  moren_passwd="yungui-2022"
  if [ "$moren_passwd" == "$password" ]; then
    exit 1
  fi
  json_data='{"username":"'$username'","password":"'$password'","SECRET_KEY":"'$SECRET_KEY'"}'
  http_rest=$(curl -s -m 10 -X POST -H "'Content-type':'application/json'" -d "$json_data" $vpn_user_login)
  echo $http_rest
  if [ "$http_rest" == "ok" ]; then
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