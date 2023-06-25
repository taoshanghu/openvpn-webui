#!/bin/sh

if [ "W$WORK_DIR" != "W" ]; then
  cd  $WORK_DIR
fi

mep="/opt/ip_management/network_scanning.py"

chmod -x $mep

web_pid() {
  gunicorn_pid=$(ps -ef |grep python3 |grep gunicorn |grep -v "grep" |awk '{print $2}')
  openvpn_service_pid=$(ps -ef |grep "/opt/ip_management/bin/openvpn_server.py" |grep -v "grep" |awk '{print $2}')
}

mep_pid() {
  mes_sending_job_pid=$(ps -ef |grep python3 |grep $mep |grep -v "grep" |awk '{print $2}')
}

web_start() {
  web_pid
  if [ "W$gunicorn_pid" == "W" ]; then
    gunicorn ip_management.wsgi -c  gunicorn_config.py  >> run.log 2>&1 &
    /opt/ip_management/bin/openvpn_server.py 1 > /dev/null 2 > /opt/ip_management/bin/openvpn-service.err &
    echo "gunicorn running successfully"
  else
    echo "gunicorn running"
  fi
}



web_stop() {
  web_pid
  if [ "W$gunicorn_pid" == "W" ]; then
    echo "gunicorn stop"
  else
    kill $gunicorn_pid
    kill $openvpn_service_pid
    echo "gunicorn stop successfully"
  fi
}

web_status() {
  web_pid
  if [ "W$gunicorn_pid" == "W" ]; then
    echo "gunicorn not running"
  else
    echo "gunicorn running"
  fi
}

mep_start() {
  mep_pid
  if [ "W$mes_sending_job_pid" == "W" ]; then
    python3 $mep &
    echo "$mep running successfully"
  else
    echo "$mep running"
  fi
}

mep_stop() {
  mep_pid
  if [ "W$mes_sending_job_pid" == "W" ]; then
    echo "$mep stop"
  else
    kill mes_sending_job_pid
    echo "$mep stop successfully"
  fi
}

mep_status() {
  mep_pid
  if [ "W$mes_sending_job_pid" == "W" ]; then
    echo "$mep not running"
  else
    echo "$mep running"
  fi
}

start() {
  web_start
  sleep 5
  #mep_start
}

stop() {
  web_stop
  #mep_stop
}

status() {
  #mep_status
  web_status
}

case $1 in
status)
  status
  ;;
stop)
  stop
  ;;
start)
  start
  ;;
restart)
  stop
  start
  ;;
*)
  echo "status|start|stop|restart"
esac