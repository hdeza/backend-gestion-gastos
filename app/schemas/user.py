"""
Esquemas para Usuario
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

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

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    moneda_preferida: Optional[str] = None
    foto_perfil: Optional[str] = None

class ChangePassword(BaseModel):
    old_password: str
    new_password: str
