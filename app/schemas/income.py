"""
Esquemas para Ingreso
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

class IngresoBase(BaseModel):
    descripcion: str
    monto: Decimal
    fecha: date
    fuente: Optional[str]

class IngresoCreate(IngresoBase):
    id_categoria: Optional[int]
    id_grupo: Optional[int]

class IngresoResponse(IngresoBase):
    id_ingreso: int
    id_categoria: Optional[int]
    id_usuario: int
    id_grupo: Optional[int]
    
    class Config:
        from_attributes = True

class IngresoUpdate(BaseModel):
    descripcion: Optional[str] = None
    monto: Optional[Decimal] = None
    fecha: Optional[date] = None
    fuente: Optional[str] = None
    id_categoria: Optional[int] = None
    id_grupo: Optional[int] = None
