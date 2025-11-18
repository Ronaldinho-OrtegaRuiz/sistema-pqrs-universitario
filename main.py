"""
Bot de WhatsApp con FastAPI
"""
from fastapi import FastAPI, Request, Response, HTTPException, status, Query
from fastapi.responses import JSONResponse
from typing import Optional
from contextlib import asynccontextmanager
import logging
import asyncio

from config import settings
from models.whatsapp import WebhookPayload, Message, SendMessageRequest, SendTemplateRequest
from services.message_handler import MessageHandler
from services.whatsapp_service import WhatsAppService
from utils.security import verify_webhook_token, verify_webhook_signature, get_request_body

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

message_handler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación"""
    global message_handler
    
    # Startup
    logger.info("🚀 Iniciando aplicación...")
    message_handler = MessageHandler()
    
    # Enviar PQRS pendientes al iniciar (en background)
    try:
        asyncio.create_task(message_handler._send_pending_pqrs_on_startup())
    except Exception as e:
        logger.error(f"Error al iniciar envío de PQRS pendientes: {e}")
    
    yield
    
    # Shutdown
    logger.info("👋 Cerrando aplicación...")


app = FastAPI(
    title=settings.app_name,
    description="Bot de WhatsApp usando FastAPI y Meta WhatsApp Business API",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": f"Bienvenido a {settings.app_name}",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/webhook")
async def verify_webhook(
    mode: Optional[str] = Query(None, alias="hub.mode"),
    token: Optional[str] = Query(None, alias="hub.verify_token"),
    challenge: Optional[str] = Query(None, alias="hub.challenge")
):
    """
    Endpoint de verificación del webhook de WhatsApp
    
    WhatsApp envía una petición GET para verificar el webhook durante la configuración.
    """
    logger.info(f"Verificación de webhook - mode: {mode}, token: {token}")
    
    if mode == "subscribe" and token:
        if verify_webhook_token(token):
            logger.info("Webhook verificado correctamente")
            return Response(content=challenge, status_code=200)
        else:
            logger.warning("Token de verificación inválido")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token de verificación inválido"
            )
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Parámetros de verificación inválidos"
    )


@app.post("/webhook")
async def webhook(request: Request):
    """
    Endpoint principal para recibir webhooks de WhatsApp
    
    Procesa los mensajes recibidos y genera respuestas automáticas.
    """
    try:
        # Obtener el cuerpo de la petición
        body = await get_request_body(request)
        
        # Verificar la firma del webhook (si está configurada)
        signature = request.headers.get("X-Hub-Signature-256")
        if settings.whatsapp_app_secret:
            if not verify_webhook_signature(body, signature):
                logger.warning("Firma de webhook inválida")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Firma de webhook inválida"
                )
        
        # Parsear el payload
        import json
        payload_data = json.loads(body.decode('utf-8'))
        payload = WebhookPayload(**payload_data)
        
        logger.info(f"Webhook recibido - object: {payload.object}")
        
        # Procesar cada entrada
        for entry in payload.entry:
            for change in entry.changes:
                value = change.value
                
                # Procesar mensajes recibidos
                if value.messages:
                    for message in value.messages:
                        logger.info(f"Mensaje recibido de {message.from_}: {message.text.body if message.text else 'Sin texto'}")
                        await message_handler.process_message(message, message.from_)
                
                # Procesar estados de mensajes (entregado, leído, etc.)
                if value.statuses:
                    for status_info in value.statuses:
                        logger.info(f"Estado de mensaje: {status_info}")
        
        # WhatsApp espera una respuesta 200
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "success"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al procesar webhook: {str(e)}", exc_info=True)
        # Aún así devolvemos 200 para que WhatsApp no reintente
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "error", "message": str(e)}
        )


@app.post("/send-message")
async def send_message(request_data: SendMessageRequest):
    """
    Endpoint para enviar mensajes manualmente (útil para pruebas)
    
    - **to**: Número de teléfono del destinatario (puede incluir +, espacios, etc.)
    - **message**: Texto del mensaje a enviar
    - **preview_url**: Si se deben previsualizar URLs (opcional, por defecto False)
    """
    try:
        whatsapp_service = WhatsAppService()
        result = await whatsapp_service.send_text_message(
            to=request_data.to,
            message=request_data.message,
            preview_url=request_data.preview_url
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "success", "result": result}
        )
    except Exception as e:
        logger.error(f"Error al enviar mensaje: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/send-template")
async def send_template(request_data: SendTemplateRequest):
    """
    Endpoint para enviar mensajes de plantilla (template)
    
    **IMPORTANTE:** En modo de prueba, WhatsApp solo permite enviar mensajes de plantilla, no mensajes de texto libres.
    
    - **to**: Número de teléfono del destinatario
    - **template_name**: Nombre de la plantilla (por defecto: "hello_world")
    - **language_code**: Código de idioma (por defecto: "en_US")
    - **components**: Componentes opcionales de la plantilla
    """
    try:
        whatsapp_service = WhatsAppService()
        result = await whatsapp_service.send_template_message(
            to=request_data.to,
            template_name=request_data.template_name,
            language_code=request_data.language_code,
            components=request_data.components
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "success", "result": result}
        )
    except Exception as e:
        logger.error(f"Error al enviar template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "service": settings.app_name
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
