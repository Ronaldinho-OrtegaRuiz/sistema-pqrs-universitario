"""
Utilidades para manejo de números de teléfono
"""
import re
from typing import Optional


def normalize_phone_number(phone: str) -> str:
    """
    Normaliza un número de teléfono removiendo caracteres especiales
    
    Args:
        phone: Número de teléfono en cualquier formato
        
    Returns:
        Número normalizado (solo dígitos)
        
    Examples:
        >>> normalize_phone_number("+1 555 195 2341")
        "15551952341"
        >>> normalize_phone_number("+57 324 6537538")
        "573246537538"
    """
    # Remover todos los caracteres que no sean dígitos
    normalized = re.sub(r'\D', '', phone)
    return normalized


def format_phone_number(phone: str, country_code: Optional[str] = None) -> str:
    """
    Formatea un número de teléfono con el código de país
    
    Args:
        phone: Número de teléfono
        country_code: Código de país a agregar si no está presente
        
    Returns:
        Número formateado con código de país
    """
    normalized = normalize_phone_number(phone)
    
    # Si el número no comienza con código de país y se proporciona uno
    if country_code and not normalized.startswith(country_code):
        normalized_country = normalize_phone_number(country_code)
        if not normalized.startswith(normalized_country):
            normalized = normalized_country + normalized
    
    return normalized


# Números de prueba configurados
TEST_PHONE_NUMBERS = {
    "test": "15551952341",  # +1 555 195 2341
    "personal": "573246537538"  # +57 324 6537538
}

