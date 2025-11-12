"""
Servicio para gestión de ingresos
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.income import Ingreso
from app.schemas.income import IngresoCreate, IngresoUpdate


class IncomeService:
    """Servicio para operaciones de ingresos"""

    def __init__(self, db: Session):
        self.db = db

    def create_income(self, income_data: IngresoCreate, user_id: int) -> Ingreso:
        """Crear nuevo ingreso"""
        db_income = Ingreso(
            **income_data.dict(),
            id_usuario=user_id
        )

        self.db.add(db_income)
        self.db.commit()
        self.db.refresh(db_income)
        return db_income

    def get_income_by_id(self, income_id: int, user_id: int) -> Optional[Ingreso]:
        """Obtener ingreso por ID (del usuario o de un grupo al que pertenece)"""
        income = self.db.query(Ingreso).filter(
            Ingreso.id_ingreso == income_id
        ).first()
        
        if not income:
            return None
        
        # Si es ingreso personal del usuario
        if income.id_usuario == user_id and not income.id_grupo:
            return income
        
        # Si es ingreso de grupo, verificar que el usuario pertenece al grupo
        if income.id_grupo:
            from app.models.user_group import UsuarioGrupo
            user_in_group = self.db.query(UsuarioGrupo).filter(
                UsuarioGrupo.id_usuario == user_id,
                UsuarioGrupo.id_grupo == income.id_grupo
            ).first()
            if user_in_group:
                return income
        
        return None

    def get_incomes_by_user(self, user_id: int, skip: int = 0, limit: int = 100, personal_only: bool = False) -> List[Ingreso]:
        """Obtener todos los ingresos de un usuario (personales o todos incluyendo grupos)"""
        query = self.db.query(Ingreso).filter(
            Ingreso.id_usuario == user_id
        )
        
        if personal_only:
            query = query.filter(Ingreso.id_grupo.is_(None))
        
        return query.offset(skip).limit(limit).all()

    def get_incomes_by_group(self, group_id: int, user_id: int, skip: int = 0, limit: int = 100) -> List[Ingreso]:
        """Obtener ingresos de un grupo (solo si el usuario pertenece al grupo)"""
        # Primero verificar que el usuario pertenece al grupo
        from app.models.user_group import UsuarioGrupo
        user_in_group = self.db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_usuario == user_id,
            UsuarioGrupo.id_grupo == group_id
        ).first()

        if not user_in_group:
            return []

        return self.db.query(Ingreso).filter(
            Ingreso.id_grupo == group_id
        ).offset(skip).limit(limit).all()

    def get_all_incomes(self, skip: int = 0, limit: int = 100) -> List[Ingreso]:
        """Obtener todos los ingresos (para administradores)"""
        return self.db.query(Ingreso).offset(skip).limit(limit).all()

    def update_income(self, income_id: int, income_data: IngresoUpdate, user_id: int) -> Optional[Ingreso]:
        """Actualizar ingreso (del usuario o de un grupo al que pertenece)"""
        income = self.get_income_by_id(income_id, user_id)
        if not income:
            return None

        # Verificar que el grupo sea válido si se está actualizando
        if income_data.id_grupo is not None:
            from app.models.user_group import UsuarioGrupo
            user_in_group = self.db.query(UsuarioGrupo).filter(
                UsuarioGrupo.id_usuario == user_id,
                UsuarioGrupo.id_grupo == income_data.id_grupo
            ).first()
            if not user_in_group:
                return None

        update_data = income_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(income, field, value)

        self.db.commit()
        self.db.refresh(income)
        return income

    def delete_income(self, income_id: int, user_id: int) -> bool:
        """Eliminar ingreso (solo del usuario autenticado)"""
        income = self.get_income_by_id(income_id, user_id)
        if not income:
            return False

        self.db.delete(income)
        self.db.commit()
        return True

    def get_total_income_by_user(self, user_id: int, personal_only: bool = False) -> float:
        """Obtener el total de ingresos de un usuario (personales o todos)"""
        from sqlalchemy import func
        query = self.db.query(func.sum(Ingreso.monto)).filter(
            Ingreso.id_usuario == user_id
        )
        
        if personal_only:
            query = query.filter(Ingreso.id_grupo.is_(None))
        
        result = query.scalar()
        return float(result) if result else 0.0
    
    def get_total_income_by_group(self, group_id: int, user_id: int) -> float:
        """Obtener el total de ingresos de un grupo (solo si el usuario pertenece)"""
        from sqlalchemy import func
        from app.models.user_group import UsuarioGrupo
        
        # Verificar que el usuario pertenece al grupo
        user_in_group = self.db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_usuario == user_id,
            UsuarioGrupo.id_grupo == group_id
        ).first()
        
        if not user_in_group:
            return 0.0
        
        result = self.db.query(func.sum(Ingreso.monto)).filter(
            Ingreso.id_grupo == group_id
        ).scalar()
        
        return float(result) if result else 0.0

    def get_income_by_date_range(self, user_id: int, start_date: str, end_date: str, personal_only: bool = False) -> List[Ingreso]:
        """Obtener ingresos por rango de fechas (personales o todos)"""
        from sqlalchemy import and_
        query = self.db.query(Ingreso).filter(
            and_(
                Ingreso.id_usuario == user_id,
                Ingreso.fecha >= start_date,
                Ingreso.fecha <= end_date
            )
        )
        
        if personal_only:
            query = query.filter(Ingreso.id_grupo.is_(None))
        
        return query.all()
    
    def get_group_income_by_date_range(self, group_id: int, user_id: int, start_date: str, end_date: str) -> List[Ingreso]:
        """Obtener ingresos de grupo por rango de fechas"""
        from sqlalchemy import and_
        from app.models.user_group import UsuarioGrupo
        
        # Verificar que el usuario pertenece al grupo
        user_in_group = self.db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_usuario == user_id,
            UsuarioGrupo.id_grupo == group_id
        ).first()
        
        if not user_in_group:
            return []
        
        return self.db.query(Ingreso).filter(
            and_(
                Ingreso.id_grupo == group_id,
                Ingreso.fecha >= start_date,
                Ingreso.fecha <= end_date
            )
        ).all()
