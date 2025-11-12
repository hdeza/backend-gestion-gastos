"""
Esquemas para Invitación
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InvitacionBase(BaseModel):
    id_grupo: int
    id_usuario_invitado: Optional[int] = None

class InvitacionCreate(InvitacionBase):
    dias_expiracion: Optional[int] = 7  # Por defecto 7 días

class InvitacionResponse(BaseModel):
    id_invitacion: int
    id_grupo: int
    token: str
    link_invitacion: str
    estado: str
    fecha_creacion: datetime
    fecha_expiracion: Optional[datetime] = None
    creado_por: int
    id_usuario_invitado: Optional[int] = None
    
    class Config:
        from_attributes = True

class InvitacionDetalleResponse(InvitacionResponse):
    grupo_nombre: Optional[str] = None
    grupo_descripcion: Optional[str] = None
    creador_nombre: Optional[str] = None
    
    class Config:
        from_attributes = True

class AceptarInvitacionRequest(BaseModel):
    token: str

class QRResponse(BaseModel):
    qr_code_base64: str
    link_invitacion: str
    token: str

