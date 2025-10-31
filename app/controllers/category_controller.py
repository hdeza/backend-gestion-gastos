"""
Controlador para gestión de categorías
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.category import Categoria, TipoCategoria
from app.models.user import Usuario
from app.schemas.category import CategoriaResponse, CategoriaCreate, CategoriaUpdate
from app.services.category_service import CategoryService
from app.controllers.auth_controller import get_current_user

router = APIRouter()

@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoriaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear una nueva categoría (personal o global)
    Solo administradores pueden crear categorías globales
    """
    category_service = CategoryService(db)

    try:
        db_category = category_service.create_category(category, current_user.id_usuario)
        return db_category
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear categoría: {str(e)}"
        )

@router.get("/", response_model=List[CategoriaResponse])
async def get_user_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo: ingreso o gasto"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener categorías disponibles para el usuario (personales + globales)
    Opcional: filtrar por tipo (ingreso/gasto)
    """
    category_service = CategoryService(db)

    if tipo:
        # Validar tipo
        if tipo not in [TipoCategoria.ingreso.value, TipoCategoria.gasto.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo debe ser 'ingreso' o 'gasto'"
            )

        categories = category_service.get_categories_by_type(tipo, current_user.id_usuario, skip, limit)
    else:
        categories = category_service.get_categories_by_user(current_user.id_usuario, skip, limit)

    return categories

@router.get("/personal", response_model=List[CategoriaResponse])
async def get_personal_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener solo las categorías personales del usuario autenticado
    """
    category_service = CategoryService(db)
    categories = category_service.get_personal_categories_by_user(current_user.id_usuario, skip, limit)
    return categories

@router.get("/global", response_model=List[CategoriaResponse])
async def get_global_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Obtener todas las categorías globales (disponibles para todos)
    """
    category_service = CategoryService(db)
    categories = category_service.get_global_categories(skip, limit)
    return categories

@router.get("/{category_id}", response_model=CategoriaResponse)
async def get_category(
    category_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener una categoría específica por ID
    """
    category_service = CategoryService(db)
    category = category_service.get_category_by_id(category_id, current_user.id_usuario)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    return category

@router.put("/{category_id}", response_model=CategoriaResponse)
async def update_category(
    category_id: int,
    category_update: CategoriaUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar una categoría
    Solo el propietario puede actualizar categorías personales
    Solo administradores pueden actualizar categorías globales
    """
    category_service = CategoryService(db)

    try:
        updated_category = category_service.update_category(category_id, category_update, current_user.id_usuario)

        if not updated_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )

        return updated_category

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar categoría: {str(e)}"
        )

@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar una categoría
    Solo el propietario puede eliminar categorías personales
    Solo administradores pueden eliminar categorías globales
    No se puede eliminar si está siendo usada en gastos o ingresos
    """
    category_service = CategoryService(db)

    try:
        success = category_service.delete_category(category_id, current_user.id_usuario)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )

        return {"message": "Categoría eliminada exitosamente"}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar categoría: {str(e)}"
        )

@router.get("/{category_id}/stats", response_model=dict)
async def get_category_stats(
    category_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de uso de una categoría
    Incluye total de gastos e ingresos, y cantidades
    """
    category_service = CategoryService(db)
    stats = category_service.get_category_usage_stats(category_id, current_user.id_usuario)

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    return stats
