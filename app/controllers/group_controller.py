"""
Controlador para gestión de grupos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import Usuario
from app.models.user_group import RolGrupo
from app.schemas.group import (
    GrupoResponse, GrupoCreate, GrupoUpdate, 
    GrupoDetalleResponse, MiembroGrupoResponse
)
from app.services.group_service import GroupService
from app.controllers.auth_controller import get_current_user

router = APIRouter()

@router.post("/", response_model=GrupoResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group: GrupoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo grupo. El creador se agrega automáticamente como administrador.
    """
    group_service = GroupService(db)
    try:
        db_group = group_service.create_group(group, current_user.id_usuario)
        return db_group
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear grupo: {str(e)}"
        )

@router.get("/", response_model=List[GrupoResponse])
async def get_user_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los grupos a los que pertenece el usuario autenticado
    """
    group_service = GroupService(db)
    groups = group_service.get_user_groups(current_user.id_usuario, skip, limit)
    return groups

@router.get("/created", response_model=List[GrupoResponse])
async def get_created_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener grupos creados por el usuario autenticado
    """
    group_service = GroupService(db)
    groups = group_service.get_groups_created_by_user(current_user.id_usuario, skip, limit)
    return groups

@router.get("/{group_id}", response_model=GrupoDetalleResponse)
async def get_group(
    group_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener detalles de un grupo específico (solo si el usuario pertenece al grupo)
    """
    group_service = GroupService(db)
    
    # Verificar que el usuario pertenece al grupo
    if not group_service.is_user_in_group(group_id, current_user.id_usuario):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No perteneces a este grupo"
        )

    group = group_service.get_group_by_id(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado"
        )

    # Obtener miembros
    members = group_service.get_group_members(group_id)
    miembros_response = []
    for member in members:
        usuario = member.usuario
        miembros_response.append(MiembroGrupoResponse(
            id_usuario=usuario.id_usuario,
            nombre=usuario.nombre,
            correo=usuario.correo,
            rol=member.rol.value,
            fecha_union=member.fecha_union
        ))

    return GrupoDetalleResponse(
        id_grupo=group.id_grupo,
        nombre=group.nombre,
        descripcion=group.descripcion,
        fecha_creacion=group.fecha_creacion,
        creado_por=group.creado_por,
        creador_nombre=group.creador.nombre if group.creador else None,
        total_miembros=len(miembros_response),
        miembros=miembros_response
    )

@router.put("/{group_id}", response_model=GrupoResponse)
async def update_group(
    group_id: int,
    group_update: GrupoUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar un grupo (solo administradores pueden actualizar)
    """
    group_service = GroupService(db)
    updated_group = group_service.update_group(group_id, group_update, current_user.id_usuario)

    if not updated_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado o no tienes permisos para actualizarlo"
        )

    return updated_group

@router.delete("/{group_id}")
async def delete_group(
    group_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar un grupo (solo el creador puede eliminar)
    """
    group_service = GroupService(db)
    success = group_service.delete_group(group_id, current_user.id_usuario)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado o no tienes permisos para eliminarlo"
        )

    return {"message": "Grupo eliminado exitosamente"}

@router.get("/{group_id}/members", response_model=List[MiembroGrupoResponse])
async def get_group_members(
    group_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener miembros de un grupo (solo si el usuario pertenece al grupo)
    """
    group_service = GroupService(db)
    
    if not group_service.is_user_in_group(group_id, current_user.id_usuario):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No perteneces a este grupo"
        )

    members = group_service.get_group_members(group_id)
    miembros_response = []
    for member in members:
        usuario = member.usuario
        miembros_response.append(MiembroGrupoResponse(
            id_usuario=usuario.id_usuario,
            nombre=usuario.nombre,
            correo=usuario.correo,
            rol=member.rol.value,
            fecha_union=member.fecha_union
        ))

    return miembros_response

@router.delete("/{group_id}/members/{user_id}")
async def remove_member(
    group_id: int,
    user_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remover un miembro del grupo (solo administradores o el mismo usuario)
    """
    group_service = GroupService(db)
    
    if not group_service.is_user_in_group(group_id, current_user.id_usuario):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No perteneces a este grupo"
        )

    success = group_service.remove_user_from_group(group_id, user_id, current_user.id_usuario)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo remover al miembro. Verifica que tengas permisos o que el usuario pertenezca al grupo."
        )

    return {"message": "Miembro removido exitosamente"}

@router.put("/{group_id}/members/{user_id}/role")
async def change_member_role(
    group_id: int,
    user_id: int,
    new_role: str = Query(..., description="Nuevo rol: 'admin' o 'miembro'"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambiar el rol de un miembro (solo administradores pueden hacerlo)
    """
    group_service = GroupService(db)
    
    if new_role not in ["admin", "miembro"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rol inválido. Debe ser 'admin' o 'miembro'"
        )

    rol = RolGrupo.admin if new_role == "admin" else RolGrupo.miembro
    success = group_service.change_member_role(group_id, user_id, rol, current_user.id_usuario)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo cambiar el rol. Verifica que tengas permisos de administrador."
        )

    return {"message": f"Rol cambiado a {new_role} exitosamente"}

