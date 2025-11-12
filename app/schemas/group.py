"""
Esquemas para Grupo
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class GrupoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class GrupoCreate(GrupoBase):
    pass

class GrupoResponse(GrupoBase):
    id_grupo: int
    fecha_creacion: datetime
    creado_por: int
    
    class Config:
        from_attributes = True

class GrupoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

class MiembroGrupoResponse(BaseModel):
    id_usuario: int
    nombre: str
    correo: str
    rol: str
    fecha_union: datetime
    
    class Config:
        from_attributes = True

class GrupoDetalleResponse(GrupoResponse):
    creador_nombre: Optional[str] = None
    total_miembros: int = 0
    miembros: Optional[List[MiembroGrupoResponse]] = None
    
    class Config:
        from_attributes = True

