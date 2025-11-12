"""
Esquemas para AporteMeta
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

class AporteMetaBase(BaseModel):
    monto: Decimal
    fecha: Optional[date] = None

class AporteMetaCreate(AporteMetaBase):
    id_meta: int

class AporteMetaResponse(AporteMetaBase):
    id_aporte: int
    id_meta: int
    id_usuario: int
    
    class Config:
        from_attributes = True

class AporteMetaDetalleResponse(AporteMetaResponse):
    nombre_usuario: Optional[str] = None
    nombre_meta: Optional[str] = None
    
    class Config:
        from_attributes = True

class AporteMetaUpdate(BaseModel):
    monto: Optional[Decimal] = None
    fecha: Optional[date] = None

