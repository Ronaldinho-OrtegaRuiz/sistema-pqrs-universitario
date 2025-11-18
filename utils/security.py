"""
Utilidades de seguridad para validar webhooks de WhatsApp
"""
import hmac
import hashlib
from typing import Optional
from fastapi import Request, HTTPException, status
from config import settings


def verify_webhook_signature(payload: bytes, signature: Optional[str]) -> bool:
    """
    Verifica la firma del webhook de WhatsApp
    
    Args:
        payload: Cuerpo de la petición en bytes
        signature: Firma recibida en el header X-Hub-Signature-256
        
    Returns:
        True si la firma es válida, False en caso contrario
    """
    if not signature or not settings.whatsapp_app_secret:
        return False
    
    # WhatsApp envía la firma como "sha256=<hash>"
    try:
        received_hash = signature.replace("sha256=", "")
    except AttributeError:
        return False
    
    # Calcula el hash esperado
    expected_hash = hmac.new(
        settings.whatsapp_app_secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Compara de forma segura
    return hmac.compare_digest(received_hash, expected_hash)


def verify_webhook_token(token: str) -> bool:
    """
    Verifica el token de verificación del webhook
    
    Args:
        token: Token recibido en el query parameter
        
    Returns:
        True si el token es válido
    """
    return token == settings.whatsapp_verify_token


async def get_request_body(request: Request) -> bytes:
    """
    Obtiene el cuerpo de la petición como bytes
    
    Args:
        request: Request de FastAPI
        
    Returns:
        Cuerpo de la petición en bytes
    """
    return await request.body()


