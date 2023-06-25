#!/usr/bin/python3

import os

if "PORT" in os.environ:
    port=os.environ["PORT"]
else:
    port = 8080
bind = '0.0.0.0:%s' % str(port)    #绑定ip和端口号
backlog = 512                #监听队列
chdir = os.path.dirname(os.path.abspath(__file__))  #gunicorn要切换到的目的工作目录
timeout = 30      #超时
workers = 2    #进程数
threads = 2 #指定每个进程开启的线程数
loglevel = 'info' #日志级别，这个日志级别指的是错误日志的级别，而访问日志的级别无法设置
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"' 
accesslog = "gunicorn_access.log"      #访问日志文件
errorlog = "gunicorn_error.log"        #错误日志文件

