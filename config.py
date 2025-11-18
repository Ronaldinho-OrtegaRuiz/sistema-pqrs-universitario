"""
Configuración del bot de WhatsApp
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # FastAPI
    app_name: str = "Bot Libertador"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # WhatsApp Business API
    whatsapp_verify_token: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
    whatsapp_access_token: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    whatsapp_app_secret: str = os.getenv("WHATSAPP_APP_SECRET", "")
    whatsapp_phone_number_id: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    whatsapp_business_account_id: str = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
    whatsapp_api_version: str = os.getenv("WHATSAPP_API_VERSION", "v22.0")
    whatsapp_api_base_url: str = f"https://graph.facebook.com/{os.getenv('WHATSAPP_API_VERSION', 'v22.0')}"
    
    # Webhook
    webhook_path: str = "/webhook"
    
    # Telegram Bot (Opcional - para anuncios en canal)
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_channel_id: str = os.getenv("TELEGRAM_CHANNEL_ID", "")
    
    # Email (Para envío de PQRS usando SendGrid API)
    # SendGrid es gratuito: 100 emails/día sin necesidad de credenciales SMTP propias
    email_sendgrid_api_key: str = os.getenv("EMAIL_SENDGRID_API_KEY", "")  # API Key de SendGrid
    email_sender: str = os.getenv("EMAIL_SENDER", "noreply@ulibertadores.edu.co")  # Email desde el que aparece enviado (puede ser cualquiera)
    email_recipient: str = os.getenv("EMAIL_RECIPIENT", "andresjose.sabagh.5@gmail.com")  # Correo destino
    
    # Números de teléfono de prueba
    # Número de prueba: +1 555 195 2341 (normalizado: 15551952341)
    # Número personal: +57 324 6537538 (normalizado: 573246537538)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


