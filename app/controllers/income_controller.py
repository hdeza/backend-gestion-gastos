"""
Controlador para gestión de ingresos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.income import Ingreso
from app.models.user import Usuario
from app.schemas.income import IngresoResponse, IngresoCreate, IngresoUpdate
from app.services.income_service import IncomeService
from app.controllers.auth_controller import get_current_user

router = APIRouter()

@router.post("/", response_model=IngresoResponse, status_code=status.HTTP_201_CREATED)
async def create_income(
    income: IngresoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo ingreso para el usuario autenticado
    """
    income_service = IncomeService(db)

    # Si se especifica un grupo, verificar que el usuario pertenece a él
    if income.id_grupo:
        from app.models.user_group import UsuarioGrupo
        user_in_group = db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_usuario == current_user.id_usuario,
            UsuarioGrupo.id_grupo == income.id_grupo
        ).first()

        if not user_in_group:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No perteneces a este grupo"
            )

    try:
        db_income = income_service.create_income(income, current_user.id_usuario)
        return db_income
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear ingreso: {str(e)}"
        )

@router.get("/", response_model=List[IngresoResponse])
async def get_user_incomes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los ingresos del usuario autenticado
    """
    income_service = IncomeService(db)
    incomes = income_service.get_incomes_by_user(current_user.id_usuario, skip, limit)
    return incomes

@router.get("/group/{group_id}", response_model=List[IngresoResponse])
async def get_group_incomes(
    group_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener ingresos de un grupo específico
    """
    income_service = IncomeService(db)
    incomes = income_service.get_incomes_by_group(group_id, current_user.id_usuario, skip, limit)
    return incomes

@router.get("/{income_id}", response_model=IngresoResponse)
async def get_income(
    income_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener un ingreso específico del usuario autenticado
    """
    income_service = IncomeService(db)
    income = income_service.get_income_by_id(income_id, current_user.id_usuario)

    if not income:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingreso no encontrado"
        )

    return income

@router.put("/{income_id}", response_model=IngresoResponse)
async def update_income(
    income_id: int,
    income_update: IngresoUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar un ingreso del usuario autenticado
    """
    income_service = IncomeService(db)

    # Verificar que el grupo sea válido si se está actualizando
    if income_update.id_grupo:
        from app.models.user_group import UsuarioGrupo
        user_in_group = db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_usuario == current_user.id_usuario,
            UsuarioGrupo.id_grupo == income_update.id_grupo
        ).first()

        if not user_in_group:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No perteneces a este grupo"
            )

    updated_income = income_service.update_income(income_id, income_update, current_user.id_usuario)

    if not updated_income:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingreso no encontrado"
        )

    return updated_income

@router.delete("/{income_id}")
async def delete_income(
    income_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar un ingreso del usuario autenticado
    """
    income_service = IncomeService(db)
    success = income_service.delete_income(income_id, current_user.id_usuario)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingreso no encontrado"
        )

    return {"message": "Ingreso eliminado exitosamente"}

@router.get("/total/amount", response_model=dict)
async def get_total_income(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener el total de ingresos del usuario autenticado
    """
    income_service = IncomeService(db)
    total = income_service.get_total_income_by_user(current_user.id_usuario)

    return {"total_ingresos": total}

@router.get("/date-range/", response_model=List[IngresoResponse])
async def get_incomes_by_date_range(
    start_date: str = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Fecha de fin (YYYY-MM-DD)"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener ingresos por rango de fechas
    """
    try:
        # Validar formato de fechas
        from datetime import datetime
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')

        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de inicio debe ser anterior a la fecha de fin"
            )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha inválido. Use YYYY-MM-DD"
        )

    income_service = IncomeService(db)
    incomes = income_service.get_income_by_date_range(current_user.id_usuario, start_date, end_date)

    return incomes
