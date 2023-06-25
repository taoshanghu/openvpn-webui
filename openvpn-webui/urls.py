from django.contrib import admin
from django.urls import path, re_path
from openvpn.views import *
from openvpn.api import save_openvpn_status, vpn_conn_user_auth,vpn_user_connect,vpn_user_disconnect, kill_client

urlpatterns = [
    path('', user_login),
    path('admin/', admin.site.urls),
    path('openvpn/save_openvpn_status', save_openvpn_status),
    path('openvpn/openvpn_flow', openvpn_flow_views),
    path('openvpn/get_online_user', get_online_user),
    path('openvpn/index', index),
    path('openvpn/user', user_html),
    path('openvpn/login/',user_login),
    path('openvpn/logout',user_logout),
    path('openvpn/vpn_user_login',vpn_conn_user_auth),
    path('openvpn/user_connect',vpn_user_connect),
    path('openvpn/user_disconnect',vpn_user_disconnect),
    path('openvpn/get_all_user',get_all_user),
    path('openvpn/cruate_user/',cruate_user),
    path('openvpn/update_user_pass/',update_user_pass),
    re_path('openvpn/config_dow',config_down),
    path('openvpn/delete_user/',delete_user),
    path('openvpn/user_monitoring/',user_monitoring),
    path('openvpn/login_log/', get_user_login_log),
    path('openvpn/login_log_data/', get_user_login_log_data),
    path('openvpn/kill_client/', kill_client),
    path('openvpn/kill_user/', kill_user),
    path('openvpn/user_active/',user_active),
]