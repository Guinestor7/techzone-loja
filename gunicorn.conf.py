import multiprocessing

# Servidor WSGI
bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "techzone"

# Max requests
max_requests = 1000
max_requests_jitter = 100

# Graceful restart
graceful_timeout = 30
