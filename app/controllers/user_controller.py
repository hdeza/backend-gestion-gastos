"""
Controlador para gestión de usuarios
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import Usuario
from app.schemas.user import UsuarioResponse, UsuarioUpdate
from app.services.user_service import UserService
from app.controllers.auth_controller import get_current_user

router = APIRouter()

@router.get("/profile", response_model=UsuarioResponse)
async def get_user_profile(current_user: Usuario = Depends(get_current_user)):
    """
    Obtener perfil del usuario autenticado
    """
    return current_user

@router.put("/profile", response_model=UsuarioResponse)
async def update_user_profile(
    user_update: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar perfil del usuario autenticado
    """
    user_service = UserService(db)
    updated_user = user_service.update_user(current_user.id_usuario, user_update)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return updated_user
