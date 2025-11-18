"""
Manejador de mensajes recibidos - Sistema PQRS Universidad Los Libertadores
"""
from typing import Dict, Any, Optional
from datetime import datetime
from models.whatsapp import Message
from services.whatsapp_service import WhatsAppService
from services.announcement_service import TelegramAnnouncementService
from services.pqrs_storage import PQRSStorage
from services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)


class MessageHandler:
    """Maneja la lógica de procesamiento de mensajes para el sistema PQRS"""
    
    # Estados de la conversación
    ESTADO_INICIAL = "inicial"
    ESTADO_ESPERANDO_DEPARTAMENTO = "esperando_departamento"
    ESTADO_ESPERANDO_DESCRIPCION = "esperando_descripcion"
    ESTADO_COMPLETADO = "completado"
    
    # Departamentos disponibles
    DEPARTAMENTOS = {
        "1": {"nombre": "Tecnología", "codigo": "TEC"},
        "2": {"nombre": "Aseo y Mantenimiento", "codigo": "ASE"},
        "3": {"nombre": "Educativo", "codigo": "EDU"},
        "4": {"nombre": "Administrativo", "codigo": "ADM"},
        "5": {"nombre": "Biblioteca", "codigo": "BIB"},
        "6": {"nombre": "Seguridad", "codigo": "SEG"},
        "7": {"nombre": "Otro", "codigo": "OTR"}
    }
    
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
        # Servicio de Telegram para anuncios (opcional)
        self.telegram_service = TelegramAnnouncementService()
        # Servicio de email para envío de PQRS
        self.email_service = EmailService()
        # Almacenamiento persistente de PQRS
        self.pqrs_storage = PQRSStorage()
        # Almacenamiento en memoria del estado de las conversaciones
        # En producción, usar una base de datos
        self.conversations: Dict[str, Dict[str, Any]] = {}
    
    def _get_conversation_state(self, from_number: str) -> Dict[str, Any]:
        """Obtiene el estado de la conversación del usuario"""
        if from_number not in self.conversations:
            self.conversations[from_number] = {
                "estado": self.ESTADO_INICIAL,
                "departamento": None,
                "descripcion": None,
                "fecha_inicio": datetime.now().isoformat(),
                "pqrs_id": None
            }
        return self.conversations[from_number]
    
    def _reset_conversation(self, from_number: str) -> None:
        """Reinicia la conversación del usuario"""
        self.conversations[from_number] = {
            "estado": self.ESTADO_INICIAL,
            "departamento": None,
            "descripcion": None,
            "fecha_inicio": datetime.now().isoformat(),
            "pqrs_id": None
        }
    
    async def process_message(self, message: Message, from_number: str) -> None:
        """
        Procesa un mensaje recibido y genera una respuesta
        
        Args:
            message: Objeto Message recibido
            from_number: Número de teléfono del remitente
        """
        # Marcar mensaje como leído
        try:
            await self.whatsapp_service.mark_message_as_read(message.id)
        except Exception as e:
            logger.error(f"Error al marcar mensaje como leído: {e}")
        
        # Procesar el mensaje según su tipo
        if message.type == "text" and message.text:
            await self._handle_text_message(message.text.body, from_number)
        else:
            # Manejar otros tipos de mensajes (imágenes, audio, etc.)
            await self._handle_unsupported_message(from_number)
    
    async def _handle_text_message(self, text: str, from_number: str) -> None:
        """
        Maneja mensajes de texto según el flujo de PQRS
        
        Args:
            text: Texto del mensaje
            from_number: Número del remitente
        """
        text_lower = text.lower().strip()
        state = self._get_conversation_state(from_number)
        current_state = state["estado"]
        
        # Comando especial para reiniciar
        if text_lower in ["reiniciar", "nuevo", "empezar", "reset"]:
            self._reset_conversation(from_number)
            response = self._get_welcome_message()
            await self._send_message(from_number, response)
            return
        
        # Flujo según el estado actual
        if current_state == self.ESTADO_INICIAL:
            # Primer mensaje: preguntar por departamento
            response = self._get_department_selection_message()
            state["estado"] = self.ESTADO_ESPERANDO_DEPARTAMENTO
            
        elif current_state == self.ESTADO_ESPERANDO_DEPARTAMENTO:
            # Usuario debe elegir departamento
            dept_info = self._parse_department_choice(text)
            if dept_info:
                state["departamento"] = dept_info
                state["estado"] = self.ESTADO_ESPERANDO_DESCRIPCION
                response = f"✅ Perfecto. Has seleccionado: *{dept_info['nombre']}*\n\n" \
                          f"Por favor, describe detalladamente tu petición, queja, reclamo o sugerencia:\n\n" \
                          f"📝 (Escribe tu mensaje ahora)"
            else:
                response = "❌ Opción no válida. Por favor, elige un número del 1 al 7:\n\n" + \
                          self._get_department_list()
                
        elif current_state == self.ESTADO_ESPERANDO_DESCRIPCION:
            # Usuario describe el problema
            state["descripcion"] = text
            state["estado"] = self.ESTADO_COMPLETADO
            state["pqrs_id"] = f"PQRS-{state['departamento']['codigo']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Guardar PQRS en almacenamiento persistente
            pqrs_data = {
                "pqrs_id": state["pqrs_id"],
                "departamento": state["departamento"]["nombre"],
                "codigo_departamento": state["departamento"]["codigo"],
                "descripcion": text,
                "fecha": datetime.now().isoformat(),
                "telefono": from_number
            }
            self.pqrs_storage.add_pqrs(pqrs_data)
            
            # Detectar quejas similares (mismo departamento, descripción similar)
            similar_pqrs = self.pqrs_storage.get_similar_pqrs(
                state["departamento"]["codigo"],
                text
            )
            similar_count = len(similar_pqrs) - 1  # Restamos 1 porque la actual cuenta
            
            # Enviar anuncio a Telegram Channel SOLO si hay 2+ quejas similares (solo alertas)
            if similar_count >= 1:  # 1 similar + la actual = 2 o más en total
                enviado = await self._send_announcement_to_channel(
                    state["pqrs_id"],
                    state["departamento"]["nombre"],
                    text,
                    similar_count
                )
                
                # Si se envió exitosamente, marcar como enviado
                if enviado:
                    self.pqrs_storage.mark_as_sent(state["pqrs_id"])
            else:
                # Si es la primera queja, no enviar a Telegram
                logger.info(f"PQRS {state['pqrs_id']} es la primera queja de este tipo. No se envía a Telegram.")
            
            # Enviar correo electrónico para TODAS las PQRS
            await self._send_pqrs_email(
                pqrs_id=state["pqrs_id"],
                departamento=state["departamento"]["nombre"],
                codigo_departamento=state["departamento"]["codigo"],
                descripcion=text,
                telefono=from_number
            )
            
            response = self._get_confirmation_message(state)
            # - Enviar correo
            
        else:
            # Estado completado o desconocido
            response = "Tu PQRS ya ha sido registrada. Si necesitas crear una nueva, escribe 'nuevo' o 'reiniciar'."
        
        await self._send_message(from_number, response)
    
    def _parse_department_choice(self, text: str) -> Optional[Dict[str, Any]]:
        """Parsea la elección del departamento del usuario"""
        text_lower = text.lower().strip()
        
        # Verificar si es un número
        if text_lower.isdigit():
            num = text_lower
            if num in self.DEPARTAMENTOS:
                return self.DEPARTAMENTOS[num]
        
        # Verificar si menciona el nombre del departamento
        for key, dept in self.DEPARTAMENTOS.items():
            if dept["nombre"].lower() in text_lower or \
               dept["codigo"].lower() in text_lower:
                return dept
        
        return None
    
    def _get_welcome_message(self) -> str:
        """Mensaje de bienvenida"""
        return (
            "👋 *¡Bienvenido al Sistema de PQRS*\n"
            "*Universidad Los Libertadores*\n\n"
            "Estoy aquí para ayudarte a registrar tu Petición, Queja, Reclamo o Sugerencia.\n\n"
            "¿A qué departamento tiene que ver tu solicitud?"
        )
    
    def _get_department_selection_message(self) -> str:
        """Mensaje para seleccionar departamento"""
        welcome = self._get_welcome_message()
        dept_list = self._get_department_list()
        return f"{welcome}\n\n{dept_list}"
    
    def _get_department_list(self) -> str:
        """Lista de departamentos disponibles"""
        dept_text = "Elige una opción:\n\n"
        for key, dept in self.DEPARTAMENTOS.items():
            dept_text += f"*{key}.* {dept['nombre']}\n"
        dept_text += "\nResponde con el número o el nombre del departamento."
        return dept_text
    
    def _get_confirmation_message(self, state: Dict[str, Any]) -> str:
        """Mensaje de confirmación de PQRS registrada"""
        pqrs_id = state.get("pqrs_id", "PENDIENTE")
        dept = state.get("departamento", {}).get("nombre", "N/A")
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        return (
            "✅ *PQRS Registrada Exitosamente*\n\n"
            f"📋 *Número de referencia:* {pqrs_id}\n"
            f"🏢 *Departamento:* {dept}\n"
            f"📅 *Fecha:* {fecha}\n\n"
            "Tu solicitud ha sido dirigida al área encargada para su pronta solución.\n\n"
            "Recibirás una respuesta en el menor tiempo posible.\n\n"
            "¡Gracias por contactarnos! 🙏"
        )
    
    async def _send_pending_pqrs_on_startup(self) -> None:
        """Envía las PQRS pendientes al iniciar el servidor"""
        try:
            pending_pqrs = self.pqrs_storage.get_pending_pqrs()
            if pending_pqrs:
                logger.info(f"Enviando {len(pending_pqrs)} PQRS pendientes a Telegram...")
                for pqrs in pending_pqrs:
                    try:
                        # Obtener quejas similares
                        similar_pqrs = self.pqrs_storage.get_similar_pqrs(
                            pqrs["codigo_departamento"],
                            pqrs["descripcion"]
                        )
                        similar_count = len([s for s in similar_pqrs if s.get("pqrs_id") != pqrs["pqrs_id"]])
                        
                        # Enviar a Telegram SOLO si hay 2+ quejas similares (solo alertas)
                        if similar_count >= 1:  # 1 similar + la actual = 2 o más en total
                            enviado = await self._send_announcement_to_channel(
                                pqrs["pqrs_id"],
                                pqrs["departamento"],
                                pqrs["descripcion"],
                                similar_count
                            )
                            
                            # Si se envió exitosamente, marcar como enviado
                            if enviado:
                                self.pqrs_storage.mark_as_sent(pqrs["pqrs_id"])
                                logger.info(f"PQRS {pqrs['pqrs_id']} enviada y marcada como enviada (alerta múltiples reportes)")
                        else:
                            # Si es la primera queja, marcar como "enviada" pero no enviar (para no reintentar)
                            self.pqrs_storage.mark_as_sent(pqrs["pqrs_id"])
                            logger.info(f"PQRS {pqrs['pqrs_id']} es la primera queja. No se envía a Telegram.")
                        
                        # Pequeña pausa entre envíos para no saturar
                        import asyncio
                        await asyncio.sleep(1)
                    except Exception as e:
                        logger.error(f"Error al enviar PQRS {pqrs.get('pqrs_id')}: {e}")
        except Exception as e:
            logger.error(f"Error al procesar PQRS pendientes: {e}")
    
    async def _send_announcement_to_channel(
        self,
        pqrs_id: str,
        departamento: str,
        descripcion: str,
        similar_count: int
    ) -> bool:
        """
        Envía un anuncio al canal de Telegram
        
        Args:
            pqrs_id: ID de la PQRS
            departamento: Nombre del departamento
            descripcion: Descripción del problema
            similar_count: Cantidad de quejas similares
            
        Returns:
            True si se envió exitosamente, False en caso contrario
        """
        try:
            result = await self.telegram_service.send_pqrs_alert(
                pqrs_id=pqrs_id,
                departamento=departamento,
                descripcion=descripcion,
                cantidad_similar=similar_count
            )
            return result.get("ok", False)
        except Exception as e:
            logger.error(f"Error al enviar anuncio a Telegram: {e}")
            return False
    
    async def _send_pqrs_email(
        self,
        pqrs_id: str,
        departamento: str,
        codigo_departamento: str,
        descripcion: str,
        telefono: str
    ) -> None:
        """
        Envía un correo electrónico con la información de la PQRS
        
        Args:
            pqrs_id: ID de la PQRS
            departamento: Nombre del departamento
            codigo_departamento: Código del departamento
            descripcion: Descripción del problema
            telefono: Número de teléfono del usuario
        """
        try:
            await self.email_service.send_pqrs_email(
                pqrs_id=pqrs_id,
                departamento=departamento,
                codigo_departamento=codigo_departamento,
                descripcion=descripcion,
                telefono=telefono
            )
        except Exception as e:
            logger.error(f"Error al enviar correo para PQRS {pqrs_id}: {e}")
    
    async def _send_message(self, to: str, message: str) -> None:
        """Envía un mensaje al usuario"""
        try:
            await self.whatsapp_service.send_text_message(
                to=to,
                message=message
            )
        except Exception as e:
            logger.error(f"Error al enviar respuesta: {e}")
    
    async def _handle_unsupported_message(self, from_number: str) -> None:
        """
        Maneja mensajes no soportados (imágenes, audio, etc.)
        
        Args:
            from_number: Número del remitente
        """
        state = self._get_conversation_state(from_number)
        
        if state["estado"] == self.ESTADO_INICIAL:
            response = (
                "Por el momento solo puedo procesar mensajes de texto. "
                "Por favor, envía un mensaje de texto para iniciar tu PQRS."
            )
        else:
            response = (
                "Por el momento solo puedo procesar mensajes de texto. "
                "Por favor, continúa con texto para completar tu solicitud."
            )
        
        await self._send_message(from_number, response)
