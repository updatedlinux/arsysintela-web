# -*- encoding: utf-8 -*-


import os
from apps.pages import blueprint
from flask import render_template, request, current_app, send_from_directory, abort, session, redirect, url_for, flash
from jinja2 import TemplateNotFound
from apps.utils.client_portal_api import api_post, api_get, get_client_portal_token, get_client_portal_user


@blueprint.route('/')
def index():
    return render_template('pages/index6.html', segment='index')


@blueprint.route('/solutions/<solution_name>')
def solution_page(solution_name):
    try:
        # Map solution names to template files
        solution_templates = {
            'assistant360': 'assistant360.html',
            'condominio360': 'condominio360.html',
            'serviexpress': 'serviexpress.html',
            'intela-grid': 'intela_grid.html',
            'intela-smart': 'intela_smart.html',
        }
        
        template = solution_templates.get(solution_name)
        if template:
            segment = get_segment(request)
            return render_template("pages/" + template, segment=segment)
        else:
            return render_template('pages/page-404.html'), 404
    except TemplateNotFound:
        return render_template('pages/page-404.html'), 404
    except:
        return render_template('pages/page-500.html'), 500


@blueprint.route('/terminos')
def terminos():
    segment = get_segment(request)
    return render_template('pages/terminos.html', segment=segment)


@blueprint.route('/privacidad')
def privacidad():
    segment = get_segment(request)
    return render_template('pages/privacidad.html', segment=segment)


# ==================== Portal de Clientes ====================

@blueprint.route('/login', methods=['GET'])
def login():
    """
    Muestra la página de login del Portal de Clientes.
    Si el usuario ya tiene sesión activa, redirige a /portal-clientes.
    """
    # Si ya hay sesión activa, redirigir al dashboard
    if get_client_portal_token():
        return redirect(url_for('pages_blueprint.portal_clientes'))
    
    error = request.args.get('error', '')
    return render_template('pages/login.html', error=error, segment='login')


@blueprint.route('/login', methods=['POST'])
def login_post():
    """
    Procesa el formulario de login y autentica contra la API del Portal de Clientes.
    """
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    
    if not email or not password:
        return render_template('pages/login.html', error='Por favor, completa todos los campos.', segment='login')
    
    try:
        # Llamar a la API de login
        response_json, status_code = api_post('/auth/login', {
            'email': email,
            'password': password
        })
        
        if status_code == 200 and 'token' in response_json:
            # Login exitoso: guardar token y datos del usuario en sesión
            session['client_portal_token'] = response_json['token']
            session['client_portal_user'] = response_json.get('user', {})
            
            # Redirigir al dashboard
            return redirect(url_for('pages_blueprint.portal_clientes'))
        elif status_code in [400, 401]:
            # Error en las credenciales o validación
            error_message = response_json.get('message', 'Correo o contraseña inválidos')
            return render_template('pages/login.html', error=error_message, segment='login')
        else:
            # Otro error (500, etc.)
            error_message = response_json.get('message', 'Error al procesar la solicitud. Intenta nuevamente.')
            current_app.logger.warning(f"Login falló con código {status_code}: {error_message}")
            return render_template('pages/login.html', error=error_message, segment='login')
    
    except Exception as e:
        current_app.logger.error(f"Error en login: {str(e)}")
        return render_template('pages/login.html', error='Error al conectar con el servidor. Intenta nuevamente más tarde.', segment='login')


@blueprint.route('/logout')
def logout():
    """
    Cierra la sesión del Portal de Clientes y redirige al login.
    """
    # Eliminar datos de sesión del portal
    session.pop('client_portal_token', None)
    session.pop('client_portal_user', None)
    
    return redirect(url_for('pages_blueprint.login'))


@blueprint.route('/portal-clientes')
def portal_clientes():
    """
    Dashboard del Portal de Clientes que muestra el listado de clientes.
    Requiere autenticación (token en sesión).
    """
    # Verificar que haya sesión activa
    token = get_client_portal_token()
    if not token:
        return redirect(url_for('pages_blueprint.login', error='Por favor, inicia sesión para acceder al portal.'))
    
    user = get_client_portal_user()
    
    # Obtener parámetros de paginación
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    try:
        # Llamar a la API para obtener el listado de clientes
        response_json, status_code = api_get('/clients', {
            'page': page,
            'limit': limit
        })
        
        if status_code == 200:
            # Éxito: mostrar el dashboard con los datos
            clients = response_json.get('data', [])
            pagination = response_json.get('pagination', {})
            
            return render_template(
                'pages/portal_clientes.html',
                clients=clients,
                pagination=pagination,
                user=user,
                segment='portal-clientes'
            )
        
        elif status_code == 401:
            # Token expirado o inválido
            session.pop('client_portal_token', None)
            session.pop('client_portal_user', None)
            return redirect(url_for('pages_blueprint.login', error='Sesión expirada, por favor inicia sesión nuevamente.'))
        
        else:
            # Otro error
            error_message = response_json.get('message', 'Error al cargar los clientes.')
            return render_template(
                'pages/portal_clientes.html',
                clients=[],
                pagination={},
                user=user,
                error=error_message,
                segment='portal-clientes'
            )
    
    except Exception as e:
        current_app.logger.error(f"Error al obtener clientes: {str(e)}")
        return render_template(
            'pages/portal_clientes.html',
            clients=[],
            pagination={},
            user=user,
            error='No se pudo cargar la lista de clientes. Intenta nuevamente más tarde.',
            segment='portal-clientes'
        )


# ==================== Fin Portal de Clientes ====================


@blueprint.route('/<template>')
def route_template(template):
    try:
        # Excluir rutas del Portal de Clientes de la ruta genérica
        excluded_routes = ['portal-clientes', 'login', 'logout']
        if template in excluded_routes:
            abort(404)
        
        # Rutas especiales para iconos de Apple / favicons
        # Evitar que se intenten procesar como plantillas HTML
        if template.startswith('apple-touch-icon'):
            # Ejemplos de rutas solicitadas:
            # /apple-touch-icon.png
            # /apple-touch-icon-120x120.png
            # /apple-touch-icon-120x120-precomposed.png
            
            # Intenta servir desde la carpeta de favicons estáticos
            # current_app.root_path apunta a la carpeta de la app (apps/)
            # La carpeta static está en apps/static/favicon_io/
            favicon_dir = os.path.join(current_app.root_path, 'static', 'favicon_io')
            favicon_dir = os.path.abspath(favicon_dir)
            
            # Mapea diferentes nombres solicitados al archivo principal apple-touch-icon.png
            filename = 'apple-touch-icon.png'
            
            try:
                return send_from_directory(favicon_dir, filename)
            except Exception:
                # Si por alguna razón no existe, devolvemos 404 simple
                abort(404)
        
        # Excluir otros archivos estáticos comunes que no deberían ser plantillas
        static_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.css', '.js', '.json', '.xml', '.webmanifest')
        if template.lower().endswith(static_extensions):
            abort(404)

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/pages/FILE.html
        return render_template("pages/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('pages/page-404.html'), 404

    except:
        return render_template('pages/page-404.html'), 404


# Helper - Extract current page name from request
def get_segment(request):
    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None


@blueprint.route('/debug-ip')
def debug_ip():
    """
    Ruta de debug para verificar que la IP real del cliente se está capturando correctamente.
    Útil para verificar la configuración de ProxyFix y forwarded_allow_ips.
    Puede eliminarse en producción.
    """
    return {
        "remote_addr": request.remote_addr,
        "x_forwarded_for": request.headers.get("X-Forwarded-For"),
        "x_real_ip": request.headers.get("X-Real-IP"),
        "x_forwarded_proto": request.headers.get("X-Forwarded-Proto"),
        "x_forwarded_host": request.headers.get("X-Forwarded-Host"),
        "x_forwarded_port": request.headers.get("X-Forwarded-Port"),
    }


@blueprint.app_errorhandler(404)
def page_not_found(e):
    """
    Handler global para errores 404.
    Asegura que cualquier 404 muestre la página personalizada.
    """
    return render_template('pages/page-404.html'), 404
