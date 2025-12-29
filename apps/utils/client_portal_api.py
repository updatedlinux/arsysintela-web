# -*- encoding: utf-8 -*-

"""
Helper para interactuar con la API del Portal de Clientes.
"""

import requests
from flask import session, current_app
from typing import Optional, Dict, Tuple, Any


# Base URL de la API del Portal de Clientes
API_BASE_URL = 'https://clientes.arsystech.net/api'


def get_client_portal_token() -> Optional[str]:
    """
    Obtiene el token JWT del Portal de Clientes desde la sesión de Flask.
    
    Returns:
        str: Token JWT si existe, None si no hay sesión activa
    """
    return session.get('client_portal_token')


def get_client_portal_user() -> Optional[Dict]:
    """
    Obtiene los datos del usuario del Portal de Clientes desde la sesión.
    
    Returns:
        dict: Datos del usuario si existe, None si no hay sesión activa
    """
    return session.get('client_portal_user')


def api_get(path: str, params: Optional[Dict] = None) -> Tuple[Dict, int]:
    """
    Realiza una petición GET a la API del Portal de Clientes.
    
    Args:
        path: Ruta relativa del endpoint (ej: '/clients')
        params: Parámetros de query string (opcional)
    
    Returns:
        tuple: (response_json, status_code)
    
    Raises:
        requests.RequestException: Si hay un error en la petición HTTP
    """
    token = get_client_portal_token()
    
    url = f"{API_BASE_URL}{path}"
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


def api_post(path: str, json_data: Optional[Dict] = None) -> Tuple[Dict, int]:
    """
    Realiza una petición POST a la API del Portal de Clientes.
    
    Args:
        path: Ruta relativa del endpoint (ej: '/auth/login')
        json_data: Datos JSON para el body (opcional)
    
    Returns:
        tuple: (response_json, status_code)
    
    Raises:
        requests.RequestException: Si hay un error en la petición HTTP
    """
    token = get_client_portal_token()
    
    url = f"{API_BASE_URL}{path}"
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


def api_put(path: str, json_data: Optional[Dict] = None) -> Tuple[Dict, int]:
    """
    Realiza una petición PUT a la API del Portal de Clientes.
    
    Args:
        path: Ruta relativa del endpoint (ej: '/clients/1')
        json_data: Datos JSON para el body (opcional)
    
    Returns:
        tuple: (response_json, status_code)
    
    Raises:
        requests.RequestException: Si hay un error en la petición HTTP
    """
    token = get_client_portal_token()
    
    url = f"{API_BASE_URL}{path}"
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

