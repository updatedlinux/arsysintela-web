# -*- encoding: utf-8 -*-


import os
from apps.pages import blueprint
from flask import render_template, request, current_app, send_from_directory, abort, session, redirect, url_for, flash
from jinja2 import TemplateNotFound
from apps.utils.client_portal_api import api_post, api_get, api_put, get_client_portal_token, get_client_portal_user
from apps.utils.blog_api import get_posts, get_post_by_id, get_post_by_slug, create_post, update_post, delete_post
from flask import jsonify


@blueprint.route('/')
def index():
    """
    Página principal (HOME).
    Obtiene los últimos posts del blog para mostrar en la sección de blog.
    """
    latest_posts = []
    try:
        # Obtener los últimos 2-3 posts para la home
        response_json, status_code = get_posts(page=1, limit=3)
        if status_code == 200:
            latest_posts = response_json.get('data', [])
    except Exception as e:
        current_app.logger.error(f"Error al obtener posts para la home: {str(e)}")
        # Si falla, simplemente no mostrar posts (latest_posts queda vacío)
    
    return render_template('pages/index6.html', segment='index', latest_posts=latest_posts)


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
    Dashboard del Portal de Clientes.
    - Si el usuario tiene rol 'admin': muestra listado de clientes
    - Si el usuario tiene rol 'user': muestra productos asociados a su ID de cliente
    Requiere autenticación (token en sesión).
    """
    # Verificar que haya sesión activa
    token = get_client_portal_token()
    if not token:
        return redirect(url_for('pages_blueprint.login', error='Por favor, inicia sesión para acceder al portal.'))
    
    user = get_client_portal_user()
    user_role = user.get('role', '') if user else ''
    user_id = user.get('id') if user else None
    
    try:
        # Si el usuario es 'user', obtener su cliente asociado y productos
        if user_role == 'user':
            # Llamar a la API para obtener el cliente asociado al usuario
            # El endpoint /clients/me devuelve el cliente con sus productos incluidos
            response_json, status_code = api_get('/clients/me')
            
            if status_code == 200:
                # Éxito: mostrar información del cliente y sus productos
                client_data = response_json
                products = client_data.get('products', [])
                
                return render_template(
                    'pages/portal_clientes.html',
                    client=client_data,
                    products=products,
                    user=user,
                    segment='portal-clientes',
                    is_user=True
                )
            
            elif status_code == 401:
                # Token expirado o inválido
                session.pop('client_portal_token', None)
                session.pop('client_portal_user', None)
                return redirect(url_for('pages_blueprint.login', error='Sesión expirada, por favor inicia sesión nuevamente.'))
            
            elif status_code == 404:
                # Usuario no tiene cliente asociado
                error_message = response_json.get('message', 'No se encontró un cliente asociado a tu cuenta.')
                return render_template(
                    'pages/portal_clientes.html',
                    client=None,
                    products=[],
                    user=user,
                    error=error_message,
                    segment='portal-clientes',
                    is_user=True
                )
            
            else:
                # Otro error
                error_message = response_json.get('message', 'Error al cargar la información del cliente.')
                return render_template(
                    'pages/portal_clientes.html',
                    client=None,
                    products=[],
                    user=user,
                    error=error_message,
                    segment='portal-clientes',
                    is_user=True
                )
        
        # Si el usuario es 'admin', mostrar listado de clientes
        else:
            # Obtener parámetros de paginación
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 10, type=int)
            
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
                    segment='portal-clientes',
                    is_user=False
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
                    segment='portal-clientes',
                    is_user=False
                )
    
    except Exception as e:
        current_app.logger.error(f"Error en portal_clientes: {str(e)}")
        error_msg = 'No se pudo cargar la información. Intenta nuevamente más tarde.'
        if user_role == 'user':
            return render_template(
                'pages/portal_clientes.html',
                products=[],
                user=user,
                error=error_msg,
                segment='portal-clientes',
                is_user=True
            )
        else:
            return render_template(
                'pages/portal_clientes.html',
                clients=[],
                pagination={},
                user=user,
                error=error_msg,
                segment='portal-clientes',
                is_user=False
            )


# ==================== Fin Portal de Clientes ====================

# ==================== Rutas API para Administradores ====================

@blueprint.route('/portal-clientes/create-user', methods=['POST'])
def create_user():
    """
    Crea un nuevo usuario en el sistema.
    Solo accesible para administradores.
    """
    token = get_client_portal_token()
    if not token:
        return jsonify({'error': 'No autorizado'}), 401
    
    user = get_client_portal_user()
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Solo los administradores pueden crear usuarios'}), 403
    
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email y contraseña son requeridos'}), 400
        
        # Llamar a la API para crear usuario
        response_json, status_code = api_post('/users', {
            'email': data.get('email'),
            'password': data.get('password'),
            'name': data.get('name'),
            'role': data.get('role', 'user')
        })
        
        if status_code == 201:
            return jsonify({'user': response_json}), 201
        else:
            error_message = response_json.get('message', 'Error al crear el usuario')
            return jsonify({'error': error_message}), status_code
    
    except Exception as e:
        current_app.logger.error(f"Error al crear usuario: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@blueprint.route('/portal-clientes/update-client/<int:client_id>', methods=['POST'])
def update_client(client_id):
    """
    Actualiza los datos de un cliente existente.
    Solo accesible para administradores.
    """
    token = get_client_portal_token()
    if not token:
        return jsonify({'error': 'No autorizado'}), 401
    
    user = get_client_portal_user()
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Solo los administradores pueden actualizar clientes'}), 403
    
    try:
        data = request.get_json()
        
        # Validar que al menos el nombre esté presente
        if not data.get('name'):
            return jsonify({'error': 'El nombre del cliente es requerido'}), 400
        
        # Llamar a la API para actualizar cliente
        response_json, status_code = api_put(f'/clients/{client_id}', {
            'name': data.get('name'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'company': data.get('company'),
            'notes': data.get('notes')
        })
        
        if status_code == 200:
            return jsonify({'client': response_json}), 200
        else:
            error_message = response_json.get('message', 'Error al actualizar el cliente')
            return jsonify({'error': error_message}), status_code
    
    except Exception as e:
        current_app.logger.error(f"Error al actualizar cliente: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


# ==================== Fin Rutas API para Administradores ====================

# ==================== Rutas Admin Blog ====================

def require_admin():
    """
    Helper para verificar que el usuario es admin.
    """
    token = get_client_portal_token()
    if not token:
        return None, redirect(url_for('pages_blueprint.login', error='Por favor, inicia sesión para acceder al panel de administración.'))
    
    user = get_client_portal_user()
    if not user or user.get('role') != 'admin':
        return None, redirect(url_for('pages_blueprint.portal_clientes', error='Solo los administradores pueden acceder a esta sección.'))
    
    return user, None


@blueprint.route('/portal-clientes/blog')
def blog_list():
    """
    Lista todos los posts del blog (solo admin).
    """
    user, redirect_response = require_admin()
    if redirect_response:
        return redirect_response
    
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        tag = request.args.get('tag', None)
        
        response_json, status_code = get_posts(page=page, limit=limit, tag=tag)
        
        if status_code == 200:
            posts = response_json.get('data', [])
            pagination = response_json.get('pagination', {})
            
            # El API ahora incluye isPublished en el listado
            # Asegurarnos de que todos los posts tengan isPublished (por defecto False si no viene)
            for post in posts:
                if 'isPublished' not in post:
                    post['isPublished'] = False
            
            return render_template(
                'pages/blog_list.html',
                posts=posts,
                pagination=pagination,
                user=user,
                segment='blog',
                tag=tag
            )
        elif status_code == 401:
            session.pop('client_portal_token', None)
            session.pop('client_portal_user', None)
            return redirect(url_for('pages_blueprint.login', error='Sesión expirada, por favor inicia sesión nuevamente.'))
        else:
            error_message = response_json.get('message', 'Error al cargar los posts.')
            return render_template(
                'pages/blog_list.html',
                posts=[],
                pagination={},
                user=user,
                error=error_message,
                segment='blog'
            )
    
    except Exception as e:
        current_app.logger.error(f"Error en blog_list: {str(e)}")
        return render_template(
            'pages/blog_list.html',
            posts=[],
            pagination={},
            user=user,
            error='No se pudo cargar la lista de posts. Intenta nuevamente más tarde.',
            segment='blog'
        )


@blueprint.route('/portal-clientes/blog/new', methods=['GET', 'POST'])
def blog_new():
    """
    Crea un nuevo post del blog (solo admin).
    """
    user, redirect_response = require_admin()
    if redirect_response:
        return redirect_response
    
    if request.method == 'POST':
        try:
            data = request.form
            
            # Validar campos requeridos
            required_fields = ['title', 'excerpt', 'author', 'publishedAt', 'headerImageUrl', 'contentHtml']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return render_template(
                    'pages/blog_form.html',
                    user=user,
                    error=f'Los siguientes campos son requeridos: {", ".join(missing_fields)}',
                    segment='blog',
                    post=None
                )
            
            # Preparar datos del post
            post_data = {
                'title': data.get('title'),
                'excerpt': data.get('excerpt'),
                'author': data.get('author'),
                'publishedAt': data.get('publishedAt'),
                'headerImageUrl': data.get('headerImageUrl'),
                'contentHtml': data.get('contentHtml'),
                'tag': data.get('tag') or None,
                'isPublished': data.get('isPublished') == 'true'
            }
            
            # Crear el post
            response_json, status_code = create_post(post_data)
            
            if status_code == 201:
                flash('Post creado exitosamente.', 'success')
                return redirect(url_for('pages_blueprint.blog_list'))
            elif status_code == 401:
                session.pop('client_portal_token', None)
                session.pop('client_portal_user', None)
                return redirect(url_for('pages_blueprint.login', error='Sesión expirada, por favor inicia sesión nuevamente.'))
            elif status_code == 403:
                return render_template(
                    'pages/blog_form.html',
                    user=user,
                    error='No tienes permisos para crear posts.',
                    segment='blog',
                    post=None
                )
            else:
                error_message = response_json.get('message', 'Error al crear el post.')
                return render_template(
                    'pages/blog_form.html',
                    user=user,
                    error=error_message,
                    segment='blog',
                    post=None
                )
        
        except Exception as e:
            current_app.logger.error(f"Error en blog_new POST: {str(e)}")
            return render_template(
                'pages/blog_form.html',
                user=user,
                error='Error al crear el post. Intenta nuevamente más tarde.',
                segment='blog',
                post=None
            )
    
    # GET: mostrar formulario vacío
    return render_template(
        'pages/blog_form.html',
        user=user,
        segment='blog',
        post=None
    )


@blueprint.route('/portal-clientes/blog/<int:post_id>/edit', methods=['GET', 'POST'])
def blog_edit(post_id):
    """
    Edita un post existente del blog (solo admin).
    """
    user, redirect_response = require_admin()
    if redirect_response:
        return redirect_response
    
    if request.method == 'POST':
        try:
            data = request.form
            
            # Preparar datos del post (todos opcionales para PUT)
            post_data = {}
            if data.get('title'):
                post_data['title'] = data.get('title')
            if data.get('excerpt'):
                post_data['excerpt'] = data.get('excerpt')
            if data.get('author'):
                post_data['author'] = data.get('author')
            if data.get('publishedAt'):
                post_data['publishedAt'] = data.get('publishedAt')
            if data.get('headerImageUrl'):
                post_data['headerImageUrl'] = data.get('headerImageUrl')
            if data.get('contentHtml'):
                post_data['contentHtml'] = data.get('contentHtml')
            if data.get('tag'):
                post_data['tag'] = data.get('tag')
            if 'isPublished' in data:
                post_data['isPublished'] = data.get('isPublished') == 'true'
            
            # Actualizar el post
            response_json, status_code = update_post(post_id, post_data)
            
            if status_code == 200:
                flash('Post actualizado exitosamente.', 'success')
                return redirect(url_for('pages_blueprint.blog_list'))
            elif status_code == 401:
                session.pop('client_portal_token', None)
                session.pop('client_portal_user', None)
                return redirect(url_for('pages_blueprint.login', error='Sesión expirada, por favor inicia sesión nuevamente.'))
            elif status_code == 403:
                return render_template(
                    'pages/blog_form.html',
                    user=user,
                    error='No tienes permisos para editar posts.',
                    segment='blog',
                    post=None
                )
            elif status_code == 404:
                return render_template(
                    'pages/blog_form.html',
                    user=user,
                    error='Post no encontrado.',
                    segment='blog',
                    post=None
                )
            else:
                error_message = response_json.get('message', 'Error al actualizar el post.')
                # Recargar el post para mostrar el formulario con error
                post_response, _ = get_post_by_id(post_id)
                return render_template(
                    'pages/blog_form.html',
                    user=user,
                    error=error_message,
                    segment='blog',
                    post=post_response if isinstance(post_response, dict) else None
                )
        
        except Exception as e:
            current_app.logger.error(f"Error en blog_edit POST: {str(e)}")
            return render_template(
                'pages/blog_form.html',
                user=user,
                error='Error al actualizar el post. Intenta nuevamente más tarde.',
                segment='blog',
                post=None
            )
    
    # GET: cargar el post y mostrar formulario
    try:
        response_json, status_code = get_post_by_id(post_id)
        
        if status_code == 200:
            return render_template(
                'pages/blog_form.html',
                user=user,
                segment='blog',
                post=response_json
            )
        elif status_code == 404:
            flash('Post no encontrado.', 'error')
            return redirect(url_for('pages_blueprint.blog_list'))
        else:
            error_message = response_json.get('message', 'Error al cargar el post.')
            return render_template(
                'pages/blog_form.html',
                user=user,
                error=error_message,
                segment='blog',
                post=None
            )
    
    except Exception as e:
        current_app.logger.error(f"Error en blog_edit GET: {str(e)}")
        flash('Error al cargar el post.', 'error')
        return redirect(url_for('pages_blueprint.blog_list'))


@blueprint.route('/portal-clientes/blog/<int:post_id>/delete', methods=['POST'])
def blog_delete(post_id):
    """
    Elimina un post del blog (solo admin).
    """
    user, redirect_response = require_admin()
    if redirect_response:
        return redirect_response
    
    try:
        response_json, status_code = delete_post(post_id)
        
        if status_code == 200:
            flash('Post eliminado exitosamente.', 'success')
        elif status_code == 401:
            session.pop('client_portal_token', None)
            session.pop('client_portal_user', None)
            return redirect(url_for('pages_blueprint.login', error='Sesión expirada, por favor inicia sesión nuevamente.'))
        elif status_code == 403:
            flash('No tienes permisos para eliminar posts.', 'error')
        elif status_code == 404:
            flash('Post no encontrado.', 'error')
        else:
            error_message = response_json.get('message', 'Error al eliminar el post.')
            flash(error_message, 'error')
    
    except Exception as e:
        current_app.logger.error(f"Error en blog_delete: {str(e)}")
        flash('Error al eliminar el post. Intenta nuevamente más tarde.', 'error')
    
    return redirect(url_for('pages_blueprint.blog_list'))


# ==================== Fin Rutas Admin Blog ====================

# ==================== Rutas Públicas del Blog ====================

@blueprint.route('/blog')
def blog_public():
    """
    Listado público de posts del blog con paginación.
    """
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 9, type=int)
        tag = request.args.get('tag', None)
        
        response_json, status_code = get_posts(page=page, limit=limit, tag=tag)
        
        if status_code == 200:
            posts = response_json.get('data', [])
            pagination = response_json.get('pagination', {})
            
            return render_template(
                'pages/blog.html',
                posts=posts,
                pagination=pagination,
                segment='blog',
                tag=tag
            )
        else:
            # Si hay error, mostrar página vacía con mensaje
            error_message = response_json.get('message', 'Error al cargar los posts.')
            current_app.logger.error(f"Error al cargar posts en /blog: {error_message}")
            return render_template(
                'pages/blog.html',
                posts=[],
                pagination={},
                segment='blog',
                error='No se pudieron cargar los posts. Intenta nuevamente más tarde.'
            )
    
    except Exception as e:
        current_app.logger.error(f"Error en blog_public: {str(e)}")
        return render_template(
            'pages/blog.html',
            posts=[],
            pagination={},
            segment='blog',
            error='No se pudo cargar la lista de posts. Intenta nuevamente más tarde.'
        )


@blueprint.route('/blog/<slug>')
def blog_post_detail(slug):
    """
    Detalle de un post individual del blog.
    """
    try:
        response_json, status_code = get_post_by_slug(slug)
        
        if status_code == 200:
            post = response_json
            return render_template(
                'pages/blog-detail.html',
                post=post,
                segment='blog'
            )
        elif status_code == 404:
            # Post no encontrado, mostrar 404
            return render_template('pages/page-404.html'), 404
        else:
            # Otro error
            error_message = response_json.get('message', 'Error al cargar el post.')
            current_app.logger.error(f"Error al cargar post {slug}: {error_message}")
            return render_template('pages/page-404.html'), 404
    
    except Exception as e:
        current_app.logger.error(f"Error en blog_post_detail: {str(e)}")
        return render_template('pages/page-404.html'), 404


# ==================== Fin Rutas Públicas del Blog ====================


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
