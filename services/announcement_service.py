"""
Servicio para enviar anuncios a Telegram Channel
"""
import httpx
from typing import Optional, Dict, Any
import logging
from config import settings

logger = logging.getLogger(__name__)


class TelegramAnnouncementService:
    """Servicio para enviar anuncios a un canal de Telegram"""
    
    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.channel_id = settings.telegram_channel_id
        if self.bot_token:
            self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        else:
            self.base_url = None
    
    async def send_announcement(self, message: str) -> Dict[str, Any]:
        """
        Envía un anuncio al canal de Telegram
        
        Args:
            message: Mensaje a enviar
            
        Returns:
            Respuesta de la API de Telegram
        """
        if not self.bot_token or not self.channel_id or not self.base_url:
            logger.warning("Telegram no configurado. Saltando envío de anuncio.")
            return {"ok": False, "error": "Telegram no configurado"}
        
        url = f"{self.base_url}/sendMessage"
        
        payload = {
            "chat_id": self.channel_id,
            "text": message,
            "parse_mode": "HTML"  # Permite formato HTML básico
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=30.0)
                response.raise_for_status()
                result = response.json()
                
                # Si es exitoso, retornar
                if result.get("ok"):
                    return result
                
                # Si falla, probar diferentes formatos
                error_desc = result.get("description", "")
                if "chat not found" in error_desc.lower():
                    logger.warning(f"ID del canal '{self.channel_id}' no encontrado. Intentando formatos alternativos...")
                    
                    # Probar sin @ si lo tiene
                    alternative_ids = []
                    if self.channel_id.startswith("@"):
                        alternative_ids.append(self.channel_id[1:])  # Sin @
                    else:
                        alternative_ids.append(f"@{self.channel_id}")  # Con @
                    
                    for alt_id in alternative_ids:
                        logger.info(f"Probando con ID alternativo: {alt_id}")
                        alt_payload = {**payload, "chat_id": alt_id}
                        try:
                            alt_response = await client.post(url, json=alt_payload, timeout=30.0)
                            alt_result = alt_response.json()
                            if alt_result.get("ok"):
                                logger.info(f"✅ Éxito con ID alternativo: {alt_id}")
                                # Actualizar el ID configurado
                                self.channel_id = alt_id
                                return alt_result
                        except Exception:
                            continue
                    
                    logger.error(f"No se pudo encontrar el canal con ningún formato. Error: {error_desc}")
                    logger.error("Verifica que:")
                    logger.error("1. El bot sea ADMINISTRADOR del canal")
                    logger.error("2. El ID del canal sea correcto (@alertas_libertadores o ID numérico)")
                
                return {"ok": False, "error": error_desc}
            except httpx.HTTPStatusError as e:
                logger.error(f"Error al enviar anuncio a Telegram: {e.response.status_code}")
                if e.response.text:
                    logger.error(f"Detalle: {e.response.text}")
                return {"ok": False, "error": str(e)}
            except httpx.RequestError as e:
                logger.error(f"Error de conexión con Telegram: {str(e)}")
                return {"ok": False, "error": str(e)}
    
    async def send_pqrs_alert(
        self,
        pqrs_id: str,
        departamento: str,
        descripcion: str,
        cantidad_similar: int = 0
    ) -> Dict[str, Any]:
        """
        Envía una alerta de PQRS al canal
        
        Args:
            pqrs_id: ID de la PQRS
            departamento: Departamento afectado
            descripcion: Descripción del problema
            cantidad_similar: Cantidad de quejas similares (para alertas)
            
        Returns:
            Respuesta de la API
        """
        if cantidad_similar > 0:
            message = (
                f"⚠️ <b>ALERTA - Múltiples reportes similares</b>\n\n"
                f"📋 Se han recibido <b>{cantidad_similar + 1} quejas similares</b> sobre:\n\n"
                f"🏢 <b>Departamento:</b> {departamento}\n"
                f"📝 <b>Problema:</b> {descripcion[:100]}...\n"
                f"🆔 <b>Última PQRS:</b> {pqrs_id}\n\n"
                f"Se requiere atención inmediata."
            )
        else:
            message = (
                f"📢 <b>Nueva PQRS registrada</b>\n\n"
                f"🏢 <b>Departamento:</b> {departamento}\n"
                f"🆔 <b>ID:</b> {pqrs_id}\n"
                f"📝 <b>Descripción:</b> {descripcion[:200]}...\n\n"
                f"Se ha dirigido al área encargada."
            )
        
        return await self.send_announcement(message)
    
    async def send_general_announcement(self, title: str, message: str) -> Dict[str, Any]:
        """
        Envía un anuncio general al canal
        
        Args:
            title: Título del anuncio
            message: Contenido del anuncio
            
        Returns:
            Respuesta de la API
        """
        formatted_message = f"📢 <b>{title}</b>\n\n{message}"
        return await self.send_announcement(formatted_message)

