# -*- encoding: utf-8 -*-


bind = '0.0.0.0:5005'
workers = 1
accesslog = '-'
loglevel = 'debug'
capture_output = True
enable_stdio_inheritance = True

# Configurar IPs confiables para encabezados X-Forwarded-*
# Solo confiar en los encabezados cuando la petición viene del Nginx Proxy Manager
forwarded_allow_ips = '10.200.1.250'
