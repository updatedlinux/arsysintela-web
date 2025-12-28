# -*- encoding: utf-8 -*-


import os
from apps.pages import blueprint
from flask import render_template, request, current_app, send_from_directory, abort
from jinja2 import TemplateNotFound


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


@blueprint.route('/<template>')
def route_template(template):
    try:
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
