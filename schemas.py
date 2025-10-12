from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

# Schemas para autenticación
class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr
    moneda_preferida: Optional[str] = "COP"

class UsuarioCreate(UsuarioBase):
    contrasena: str

class UsuarioResponse(UsuarioBase):
    id_usuario: int
    fecha_registro: datetime
    foto_perfil: Optional[str]
    tipo_usuario: str
    
    class Config:
        from_attributes = True

class UsuarioLogin(BaseModel):
    correo: EmailStr
    contrasena: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    correo: Optional[str] = None

# Schemas para categorías
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

# Schemas para gastos
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

# Schemas para ingresos
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

# Schemas para metas
class MetaBase(BaseModel):
    nombre: str
    monto_objetivo: Decimal
    fecha_inicio: Optional[date]
    fecha_fin: Optional[date]
    estado: str

class MetaCreate(MetaBase):
    id_grupo: Optional[int]

class MetaResponse(MetaBase):
    id_meta: int
    monto_acumulado: Decimal
    id_usuario: Optional[int]
    id_grupo: Optional[int]
    
    class Config:
        from_attributes = True

# Schemas para grupos
class GrupoBase(BaseModel):
    nombre: str
    descripcion: Optional[str]

class GrupoCreate(GrupoBase):
    pass

class GrupoResponse(GrupoBase):
    id_grupo: int
    fecha_creacion: datetime
    creado_por: int
    
    class Config:
        from_attributes = True
