"""
Servicio de almacenamiento de PQRS
"""
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

PQRS_FILE = "pqrs_data.json"


class PQRSStorage:
    """Maneja el almacenamiento persistente de PQRS"""
    
    def __init__(self):
        self.file_path = PQRS_FILE
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Asegura que el archivo existe"""
        if not os.path.exists(self.file_path):
            self._save_pqrs([])
    
    def _load_pqrs(self) -> List[Dict[str, Any]]:
        """Carga las PQRS desde el archivo"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            return []
        except Exception as e:
            logger.error(f"Error al cargar PQRS: {e}")
            return []
    
    def _save_pqrs(self, pqrs_list: List[Dict[str, Any]]) -> None:
        """Guarda las PQRS en el archivo"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(pqrs_list, f, indent=2, ensure_ascii=False)
            
            # Copiar también a dashboard/public para que el dashboard lo lea
            dashboard_public_path = os.path.join("dashboard", "public", "pqrs_data.json")
            if os.path.exists("dashboard"):
                try:
                    # Asegurar que el directorio existe
                    os.makedirs(os.path.dirname(dashboard_public_path), exist_ok=True)
                    with open(dashboard_public_path, 'w', encoding='utf-8') as f:
                        json.dump(pqrs_list, f, indent=2, ensure_ascii=False)
                    logger.debug(f"PQRS copiadas a {dashboard_public_path}")
                except Exception as e:
                    logger.warning(f"No se pudo copiar a dashboard/public: {e}")
        except Exception as e:
            logger.error(f"Error al guardar PQRS: {e}")
    
    def add_pqrs(self, pqrs_data: Dict[str, Any]) -> None:
        """Agrega una nueva PQRS"""
        pqrs_list = self._load_pqrs()
        pqrs_data["enviado_telegram"] = False
        pqrs_data["fecha_registro"] = datetime.now().isoformat()
        pqrs_list.append(pqrs_data)
        self._save_pqrs(pqrs_list)
        logger.info(f"PQRS guardada: {pqrs_data.get('pqrs_id')}")
    
    def mark_as_sent(self, pqrs_id: str) -> None:
        """Marca una PQRS como enviada a Telegram"""
        pqrs_list = self._load_pqrs()
        for pqrs in pqrs_list:
            if pqrs.get("pqrs_id") == pqrs_id:
                pqrs["enviado_telegram"] = True
                pqrs["fecha_envio_telegram"] = datetime.now().isoformat()
                break
        self._save_pqrs(pqrs_list)
        logger.info(f"PQRS {pqrs_id} marcada como enviada")
    
    def get_pending_pqrs(self) -> List[Dict[str, Any]]:
        """Obtiene las PQRS pendientes de enviar a Telegram"""
        pqrs_list = self._load_pqrs()
        return [pqrs for pqrs in pqrs_list if not pqrs.get("enviado_telegram", False)]
    
    def get_all_pqrs(self) -> List[Dict[str, Any]]:
        """Obtiene todas las PQRS"""
        return self._load_pqrs()
    
    def get_similar_pqrs(self, codigo_departamento: str, descripcion: str, 
                        similarity_threshold: int = 2, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtiene PQRS similares para detectar quejas repetidas"""
        pqrs_list = self._load_pqrs()
        
        # Filtrar por departamento y ordenar por fecha (más recientes primero)
        dept_pqrs = [
            pqrs for pqrs in pqrs_list 
            if pqrs.get("codigo_departamento") == codigo_departamento
        ]
        dept_pqrs = sorted(dept_pqrs, key=lambda x: x.get("fecha_registro", ""), reverse=True)[:limit]
        
        # Filtrar por similitud
        descripcion_words = set(descripcion.lower().split())
        similar_pqrs = []
        
        for pqrs in dept_pqrs:
            pqrs_desc = pqrs.get("descripcion", "").lower().split()
            pqrs_words = set(pqrs_desc)
            common_words = descripcion_words.intersection(pqrs_words)
            if len(common_words) >= similarity_threshold:
                similar_pqrs.append(pqrs)
        
        return similar_pqrs

