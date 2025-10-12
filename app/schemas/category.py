"""
Esquemas para Categoría
"""
from pydantic import BaseModel
from typing import Optional

class CategoriaBase(BaseModel):
    nombre: str
    tipo: str
    color: Optional[str]
    icono: Optional[str]

class CategoriaCreate(CategoriaBase):
    es_global: bool = False

class CategoriaResponse(CategoriaBase):
    id_categoria: int
    es_global: bool
    id_usuario: Optional[int]
    
    class Config:
        from_attributes = True

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    color: Optional[str] = None
    icono: Optional[str] = None
