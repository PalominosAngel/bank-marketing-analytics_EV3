"""Modelos de respuesta simplificados para documentación automática."""
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
