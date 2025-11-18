"""
Modelos de datos para la API de WhatsApp
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Contact(BaseModel):
    """Modelo de contacto"""
    profile: Optional[Dict[str, Any]] = None
    wa_id: Optional[str] = None


class Text(BaseModel):
    """Modelo de texto"""
    body: str


class Message(BaseModel):
    """Modelo de mensaje"""
    from_: str = Field(..., alias="from")
    id: str
    timestamp: str
    text: Optional[Text] = None
    type: str
    
    class Config:
        populate_by_name = True


class Value(BaseModel):
    """Modelo de valor en webhook"""
    messaging_product: str
    metadata: Dict[str, Any]
    contacts: Optional[List[Contact]] = None
    messages: Optional[List[Message]] = None
    statuses: Optional[List[Dict[str, Any]]] = None


class Change(BaseModel):
    """Modelo de cambio en webhook"""
    value: Value
    field: str


class Entry(BaseModel):
    """Modelo de entrada en webhook"""
    id: str
    changes: List[Change]


class WebhookPayload(BaseModel):
    """Modelo completo del payload del webhook"""
    object: str
    entry: List[Entry]


class SendMessageRequest(BaseModel):
    """Modelo para enviar mensaje"""
    to: str
    message: str
    preview_url: Optional[bool] = False


class SendTemplateRequest(BaseModel):
    """Modelo para enviar mensaje de plantilla"""
    to: str
    template_name: str = "hello_world"
    language_code: str = "en_US"
    components: Optional[List[Dict[str, Any]]] = None


class SendMessageResponse(BaseModel):
    """Modelo de respuesta al enviar mensaje"""
    messaging_product: str
    contacts: List[Dict[str, Any]]
    messages: List[Dict[str, Any]]
