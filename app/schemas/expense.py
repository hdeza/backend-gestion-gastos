"""
Esquemas para Gasto
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

class GastoBase(BaseModel):
    descripcion: str
    monto: Decimal
    fecha: date
    metodo_pago: Optional[str]
    nota: Optional[str]
    recurrente: bool = False

class GastoCreate(GastoBase):
    id_categoria: Optional[int]
    id_grupo: Optional[int]

class GastoResponse(GastoBase):
    id_gasto: int
    id_categoria: Optional[int]
    id_usuario: int
    id_grupo: Optional[int]
    
    class Config:
        from_attributes = True

class GastoUpdate(BaseModel):
    descripcion: Optional[str] = None
    monto: Optional[Decimal] = None
    fecha: Optional[date] = None
    metodo_pago: Optional[str] = None
    nota: Optional[str] = None
    recurrente: Optional[bool] = None
    id_categoria: Optional[int] = None
    id_grupo: Optional[int] = None
