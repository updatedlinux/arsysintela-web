# -*- encoding: utf-8 -*-

"""
Helper para interactuar con la API del Blog de Arsys Intela.
"""

import requests
import os
from flask import session, current_app
from typing import Optional, Dict, Tuple, Any
from apps.utils.client_portal_api import get_client_portal_token


# Base URL de la API del Blog
BLOG_API_BASE_URL = os.environ.get('BLOG_API_BASE_URL', 'https://blog.arsystech.net/api')


def blog_api_get(path: str, params: Optional[Dict] = None) -> Tuple[Dict, int]:
    """
    Realiza una petición GET a la API del Blog.
    
    Args:
        path: Ruta relativa del endpoint (ej: '/posts')
        params: Parámetros de query string (opcional)
    
    Returns:
        tuple: (response_json, status_code)
    
    Raises:
        requests.RequestException: Si hay un error en la petición HTTP
    """
    token = get_client_portal_token()
    
    url = f"{BLOG_API_BASE_URL}{path}"
    headers = {}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        # Intentar parsear JSON, si falla devolver texto
        try:
            response_json = response.json()
        except ValueError:
            response_json = {'message': response.text}
        
        return response_json, response.status_code
    
    except requests.RequestException as e:
        current_app.logger.error(f"Error en petición GET a {url}: {str(e)}")
        raise


def blog_api_post(path: str, json_data: Optional[Dict] = None) -> Tuple[Dict, int]:
    """
    Realiza una petición POST a la API del Blog.
    
    Args:
        path: Ruta relativa del endpoint (ej: '/posts')
        json_data: Datos JSON para el body (opcional)
    
    Returns:
        tuple: (response_json, status_code)
    
    Raises:
        requests.RequestException: Si hay un error en la petición HTTP
    """
    token = get_client_portal_token()
    
    url = f"{BLOG_API_BASE_URL}{path}"
    headers = {'Content-Type': 'application/json'}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.post(url, headers=headers, json=json_data, timeout=10)
        
        # Intentar parsear JSON, si falla devolver texto
        try:
            response_json = response.json()
        except ValueError:
            response_json = {'message': response.text}
        
        return response_json, response.status_code
    
    except requests.RequestException as e:
        current_app.logger.error(f"Error en petición POST a {url}: {str(e)}")
        raise


def blog_api_put(path: str, json_data: Optional[Dict] = None) -> Tuple[Dict, int]:
    """
    Realiza una petición PUT a la API del Blog.
    
    Args:
        path: Ruta relativa del endpoint (ej: '/posts/1')
        json_data: Datos JSON para el body (opcional)
    
    Returns:
        tuple: (response_json, status_code)
    
    Raises:
        requests.RequestException: Si hay un error en la petición HTTP
    """
    token = get_client_portal_token()
    
    url = f"{BLOG_API_BASE_URL}{path}"
    headers = {'Content-Type': 'application/json'}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.put(url, headers=headers, json=json_data, timeout=10)
        
        # Intentar parsear JSON, si falla devolver texto
        try:
            response_json = response.json()
        except ValueError:
            response_json = {'message': response.text}
        
        return response_json, response.status_code
    
    except requests.RequestException as e:
        current_app.logger.error(f"Error en petición PUT a {url}: {str(e)}")
        raise


def blog_api_delete(path: str) -> Tuple[Dict, int]:
    """
    Realiza una petición DELETE a la API del Blog.
    
    Args:
        path: Ruta relativa del endpoint (ej: '/posts/1')
    
    Returns:
        tuple: (response_json, status_code)
    
    Raises:
        requests.RequestException: Si hay un error en la petición HTTP
    """
    token = get_client_portal_token()
    
    url = f"{BLOG_API_BASE_URL}{path}"
    headers = {}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.delete(url, headers=headers, timeout=10)
        
        # Intentar parsear JSON, si falla devolver texto
        try:
            response_json = response.json()
        except ValueError:
            response_json = {'message': response.text}
        
        return response_json, response.status_code
    
    except requests.RequestException as e:
        current_app.logger.error(f"Error en petición DELETE a {url}: {str(e)}")
        raise


# Funciones de alto nivel para facilitar el uso

def get_posts(page: int = 1, limit: int = 10, tag: Optional[str] = None) -> Tuple[Dict, int]:
    """
    Obtiene la lista de posts con paginación.
    
    Args:
        page: Número de página (default: 1)
        limit: Cantidad de posts por página (default: 10)
        tag: Tag para filtrar (opcional)
    
    Returns:
        tuple: (response_json, status_code)
    """
    params = {'page': page, 'limit': limit}
    if tag:
        params['tag'] = tag
    
    return blog_api_get('/posts', params)


def get_post_by_slug(slug: str) -> Tuple[Dict, int]:
    """
    Obtiene un post completo por su slug.
    
    Args:
        slug: Slug del post
    
    Returns:
        tuple: (response_json, status_code)
    """
    return blog_api_get(f'/posts/{slug}')


def get_post_by_id(post_id: int) -> Tuple[Dict, int]:
    """
    Obtiene un post completo por su ID.
    Primero busca el post en el listado para obtener su slug, luego obtiene el post completo.
    Nota: La API del blog no tiene endpoint directo por ID, así que buscamos en el listado.
    """
    # Buscar el post en el listado para obtener su slug
    # Intentamos con varias páginas si es necesario
    for page in range(1, 11):  # Buscar en las primeras 10 páginas
        response_json, status_code = get_posts(page=page, limit=100)
        if status_code == 200:
            posts = response_json.get('data', [])
            for post in posts:
                if post.get('id') == post_id:
                    # Obtener el post completo por slug
                    slug = post.get('slug')
                    if slug:
                        return get_post_by_slug(slug)
            # Si no encontramos más posts, salir
            if len(posts) < 100:
                break
        else:
            break
    
    return {'message': 'Post no encontrado'}, 404


def create_post(post_data: Dict) -> Tuple[Dict, int]:
    """
    Crea un nuevo post.
    
    Args:
        post_data: Diccionario con los datos del post
    
    Returns:
        tuple: (response_json, status_code)
    """
    return blog_api_post('/posts', post_data)


def update_post(post_id: int, post_data: Dict) -> Tuple[Dict, int]:
    """
    Actualiza un post existente.
    
    Args:
        post_id: ID del post a actualizar
        post_data: Diccionario con los datos a actualizar
    
    Returns:
        tuple: (response_json, status_code)
    """
    return blog_api_put(f'/posts/{post_id}', post_data)


def delete_post(post_id: int) -> Tuple[Dict, int]:
    """
    Elimina un post.
    
    Args:
        post_id: ID del post a eliminar
    
    Returns:
        tuple: (response_json, status_code)
    """
    return blog_api_delete(f'/posts/{post_id}')

