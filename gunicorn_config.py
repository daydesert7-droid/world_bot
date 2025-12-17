# gunicorn_config.py
import multiprocessing

# Количество worker процессов
workers = 1  # Для бесплатного тарифа Render.com достаточно 1 worker
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Логирование
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Биндинг
bind = '0.0.0.0:5000'