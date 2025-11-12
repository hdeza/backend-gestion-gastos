"""
Esquemas para Meta
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

class MetaBase(BaseModel):
    nombre: str
    monto_objetivo: Decimal
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[str] = "activa"

class MetaCreate(MetaBase):
    id_grupo: Optional[int] = None

class MetaResponse(MetaBase):
    id_meta: int
    monto_acumulado: Decimal
    id_usuario: Optional[int]
    id_grupo: Optional[int]
    
    class Config:
        from_attributes = True

class MetaUpdate(BaseModel):
    nombre: Optional[str] = None
    monto_objetivo: Optional[Decimal] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[str] = None
    id_grupo: Optional[int] = None

class MetaDetalleResponse(MetaResponse):
    porcentaje_completado: Optional[float] = None
    total_aportes: Optional[int] = None
    
    class Config:
        from_attributes = True

