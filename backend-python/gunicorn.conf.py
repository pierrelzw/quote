# Gunicorn 配置文件
# gunicorn.conf.py

import multiprocessing
import os

# 服务器socket
bind = "127.0.0.1:3001"
backlog = 2048

# 工作进程
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# 重启
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# 日志
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# 进程命名
proc_name = "quote-web-backend"

# 用户权限
user = "quoteapp"
group = "quoteapp"

# 其他配置
tmp_upload_dir = None
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
