# -*- encoding: utf-8 -*-


import os
from   flask_migrate import Migrate
from   flask_minify  import Minify
from   sys import exit
from   werkzeug.middleware.proxy_fix import ProxyFix
from   dotenv import load_dotenv

# Cargar variables de entorno desde .env
# Buscar .env en el directorio raíz del proyecto
basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')
load_dotenv(env_path)

from apps.config import config_dict
from apps import create_app, db

# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:

    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)

# Configurar ProxyFix para respetar encabezados X-Forwarded-* de Nginx Proxy Manager
# x_for=1: usar X-Forwarded-For (1 proxy: Nginx Proxy Manager)
# x_proto=1: usar X-Forwarded-Proto (HTTP/HTTPS)
# x_host=1: usar X-Forwarded-Host
# x_port=1: usar X-Forwarded-Port
# x_prefix=1: usar X-Forwarded-Prefix
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_port=1,
    x_prefix=1
)

Migrate(app, db)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)
    
if DEBUG:
    app.logger.info('DEBUG            = ' + str(DEBUG)             )
    app.logger.info('Page Compression = ' + 'FALSE' if DEBUG else 'TRUE' )
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT      = ' + app_config.ASSETS_ROOT )
    app.logger.info('RECAPTCHA_SITE_KEY = ' + (app_config.RECAPTCHA_SITE_KEY[:10] + '...' if app_config.RECAPTCHA_SITE_KEY else 'No configurada'))
    app.logger.info('RECAPTCHA_SECRET_KEY = ' + ('Configurada' if app_config.RECAPTCHA_SECRET_KEY else 'No configurada'))

if __name__ == "__main__":
    app.run()
