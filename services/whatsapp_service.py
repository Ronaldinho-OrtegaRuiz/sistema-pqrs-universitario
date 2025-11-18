"""
Servicio para interactuar con la API de WhatsApp
"""
import httpx
from typing import Optional, Dict, Any
from config import settings
from models.whatsapp import SendMessageRequest, SendMessageResponse
from utils.phone_utils import normalize_phone_number


class WhatsAppService:
    """Servicio para manejar operaciones con WhatsApp"""
    
    def __init__(self):
        self.base_url = settings.whatsapp_api_base_url
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.access_token = settings.whatsapp_access_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def send_text_message(
        self, 
        to: str, 
        message: str, 
        preview_url: bool = False
    ) -> Dict[str, Any]:
        """
        Envía un mensaje de texto a través de WhatsApp
        
        Args:
            to: Número de teléfono del destinatario (puede incluir +, espacios, etc.)
            message: Texto del mensaje
            preview_url: Si se deben previsualizar URLs en el mensaje
            
        Returns:
            Respuesta de la API de WhatsApp
        """
        # Normalizar el número de teléfono
        to = normalize_phone_number(to)
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": message
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_detail = f"Error al enviar mensaje: {e.response.status_code}"
                if e.response.text:
                    error_detail += f" - {e.response.text}"
                raise Exception(error_detail)
            except httpx.RequestError as e:
                raise Exception(f"Error de conexión: {str(e)}")
    
    async def send_template_message(
        self,
        to: str,
        template_name: str,
        language_code: str = "en_US",
        components: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Envía un mensaje de plantilla (template) a través de WhatsApp
        
        Args:
            to: Número de teléfono del destinatario (puede incluir +, espacios, etc.)
            template_name: Nombre de la plantilla aprobada
            language_code: Código de idioma (ej: "en_US", "es_ES")
            components: Componentes opcionales de la plantilla
            
        Returns:
            Respuesta de la API de WhatsApp
        """
        # Normalizar el número de teléfono
        to = normalize_phone_number(to)
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        if components:
            payload["template"]["components"] = components
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_detail = f"Error al enviar template: {e.response.status_code}"
                if e.response.text:
                    error_detail += f" - {e.response.text}"
                raise Exception(error_detail)
            except httpx.RequestError as e:
                raise Exception(f"Error de conexión: {str(e)}")
    
    async def mark_message_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Marca un mensaje como leído
        
        Args:
            message_id: ID del mensaje a marcar como leído
            
        Returns:
            Respuesta de la API
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_detail = f"Error al marcar mensaje como leído: {e.response.status_code}"
                if e.response.text:
                    error_detail += f" - {e.response.text}"
                raise Exception(error_detail)


