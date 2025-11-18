"""
Servicio para enviar correos electrónicos usando SendGrid API (sin necesidad de credenciales SMTP propias)
"""
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para enviar correos electrónicos con las PQRS usando SendGrid API"""
    
    def __init__(self):
        api_key = settings.email_sendgrid_api_key.strip()
        # Si la API key no empieza con "SG.", agregarlo (SendGrid siempre requiere este prefijo)
        if api_key and not api_key.startswith("SG."):
            logger.warning("La API Key de SendGrid debería empezar con 'SG.'. Intentando agregarlo automáticamente...")
            api_key = f"SG.{api_key}"
        self.api_key = api_key
        self.sender_email = settings.email_sender  # Email desde el que aparece enviado
        self.recipient_email = settings.email_recipient  # Correo destino
        self.api_url = "https://api.sendgrid.com/v3/mail/send"
    
    async def send_pqrs_email(
        self,
        pqrs_id: str,
        departamento: str,
        codigo_departamento: str,
        descripcion: str,
        telefono: str,
        fecha: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envía un correo con la información de una PQRS usando SendGrid
        
        Args:
            pqrs_id: ID de la PQRS
            departamento: Nombre del departamento
            codigo_departamento: Código del departamento
            descripcion: Descripción del problema
            telefono: Número de teléfono del usuario
            fecha: Fecha de registro (opcional)
            
        Returns:
            Diccionario con el resultado del envío
        """
        if not self.api_key:
            logger.warning("SendGrid API Key no configurada. Saltando envío de correo.")
            return {"success": False, "error": "SendGrid API Key no configurada"}
        
        if not fecha:
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        try:
            # Cuerpo del mensaje en HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
              <head>
                <meta charset="utf-8">
                <style>
                  body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                  .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
                  h2 {{ color: #0066cc; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
                  .info-box {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                  .description {{ background-color: #fff; padding: 15px; border-left: 4px solid #0066cc; margin: 10px 0; white-space: pre-wrap; }}
                  .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
                </style>
              </head>
              <body>
                <div class="container">
                  <h2>📋 Nueva PQRS Registrada</h2>
                  
                  <div class="info-box">
                    <p style="margin: 5px 0;"><strong>🆔 ID de PQRS:</strong> {pqrs_id}</p>
                    <p style="margin: 5px 0;"><strong>📅 Fecha de Registro:</strong> {fecha}</p>
                    <p style="margin: 5px 0;"><strong>🏢 Departamento:</strong> {departamento} ({codigo_departamento})</p>
                    <p style="margin: 5px 0;"><strong>📱 Teléfono:</strong> {telefono}</p>
                  </div>
                  
                  <div style="margin: 20px 0;">
                    <h3 style="color: #333;">📝 Descripción del Problema:</h3>
                    <div class="description">{descripcion}</div>
                  </div>
                  
                  <div class="footer">
                    <p>Este correo fue generado automáticamente por el Sistema de PQRS de la Universidad Los Libertadores.</p>
                    <p>Por favor, revise y atienda esta solicitud en el menor tiempo posible.</p>
                  </div>
                </div>
              </body>
            </html>
            """
            
            # Versión texto plano
            text_content = f"""
Nueva PQRS Registrada

ID de PQRS: {pqrs_id}
Fecha de Registro: {fecha}
Departamento: {departamento} ({codigo_departamento})
Teléfono: {telefono}

Descripción del Problema:
{descripcion}

---
Este correo fue generado automáticamente por el Sistema de PQRS de la Universidad Los Libertadores.
            """
            
            # Preparar payload para SendGrid API
            payload = {
                "personalizations": [
                    {
                        "to": [{"email": self.recipient_email}],
                        "subject": f"🔔 Nueva PQRS - {departamento} - {pqrs_id}"
                    }
                ],
                "from": {
                    "email": self.sender_email or "noreply@ulibertadores.edu.co",
                    "name": "Sistema PQRS - Universidad Los Libertadores"
                },
                "content": [
                    {
                        "type": "text/plain",
                        "value": text_content
                    },
                    {
                        "type": "text/html",
                        "value": html_content
                    }
                ]
            }
            
            # Headers para SendGrid
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Enviar correo usando SendGrid API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 202:
                    logger.info(f"Correo enviado exitosamente para PQRS {pqrs_id} a {self.recipient_email}")
                    return {"success": True, "message": "Correo enviado exitosamente"}
                else:
                    error_msg = f"Error al enviar correo: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {"success": False, "error": error_msg}
                    
        except Exception as e:
            error_msg = f"Error al enviar correo para PQRS {pqrs_id}: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
