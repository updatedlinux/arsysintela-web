# -*- encoding: utf-8 -*-

"""
Helper para validar Google reCAPTCHA v3.
"""

import requests
import os
from flask import current_app
from typing import Tuple, Optional


# URL de verificación de reCAPTCHA v3
RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'


def verify_recaptcha(token: str, remote_ip: Optional[str] = None) -> Tuple[bool, float, Optional[str]]:
    """
    Verifica un token de reCAPTCHA v3 con Google.
    
    Args:
        token: Token de reCAPTCHA obtenido del frontend
        remote_ip: IP del cliente (opcional, recomendado)
    
    Returns:
        tuple: (is_valid, score, error_message)
        - is_valid: True si el token es válido y el score es aceptable (>= 0.5)
        - score: Puntuación de reCAPTCHA (0.0 a 1.0)
        - error_message: Mensaje de error si hay algún problema
    """
    secret_key = os.getenv('RECAPTCHA_SECRET_KEY')
    
    if not secret_key:
        current_app.logger.warning("RECAPTCHA_SECRET_KEY no configurada")
        return False, 0.0, "Configuración de reCAPTCHA incompleta"
    
    if not token:
        return False, 0.0, "Token de reCAPTCHA no proporcionado"
    
    try:
        data = {
            'secret': secret_key,
            'response': token
        }
        
        if remote_ip:
            data['remoteip'] = remote_ip
        
        response = requests.post(RECAPTCHA_VERIFY_URL, data=data, timeout=5)
        response.raise_for_status()
        
        result = response.json()
        
        if not result.get('success', False):
            error_codes = result.get('error-codes', [])
            error_message = ', '.join(error_codes) if error_codes else 'Token inválido'
            current_app.logger.warning(f"reCAPTCHA falló: {error_message}")
            return False, 0.0, error_message
        
        score = result.get('score', 0.0)
        # reCAPTCHA v3 devuelve un score de 0.0 a 1.0
        # Normalmente se acepta >= 0.5, pero puedes ajustar este umbral
        min_score = float(os.getenv('RECAPTCHA_MIN_SCORE', '0.5'))
        is_valid = score >= min_score
        
        if not is_valid:
            current_app.logger.warning(f"reCAPTCHA score demasiado bajo: {score} (mínimo: {min_score})")
        
        return is_valid, score, None
    
    except requests.RequestException as e:
        current_app.logger.error(f"Error al verificar reCAPTCHA: {str(e)}")
        return False, 0.0, "Error al conectar con el servicio de reCAPTCHA"
    except Exception as e:
        current_app.logger.error(f"Error inesperado al verificar reCAPTCHA: {str(e)}")
        return False, 0.0, "Error al procesar la verificación de reCAPTCHA"

