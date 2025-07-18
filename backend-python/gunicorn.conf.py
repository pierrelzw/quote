# Gunicorn 生产配置 - 适用于 Render 部署
import os

# 服务器绑定
bind = "0.0.0.0:" + str(os.getenv("PORT", "5000"))
backlog = 2048

# 工作进程
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# 重启
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# 日志 - 输出到标准输出/错误（适合容器环境）
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# 进程命名
proc_name = "quote-api"

# 移除用户权限设置（在容器中不适用）
# user = "quoteapp"  # 注释掉
# group = "quoteapp"  # 注释掉

# 其他配置
tmp_upload_dir = None
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
