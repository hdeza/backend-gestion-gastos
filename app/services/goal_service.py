"""
Servicio para gestión de metas
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.goal import Meta, EstadoMeta
from app.schemas.goal import MetaCreate, MetaUpdate
from decimal import Decimal


class GoalService:
    """Servicio para operaciones de metas"""

    def __init__(self, db: Session):
        self.db = db

    def create_goal(self, goal_data: MetaCreate, user_id: int) -> Meta:
        """Crear nueva meta"""
        db_goal = Meta(
            nombre=goal_data.nombre,
            monto_objetivo=goal_data.monto_objetivo,
            monto_acumulado=Decimal('0.00'),
            fecha_inicio=goal_data.fecha_inicio,
            fecha_fin=goal_data.fecha_fin,
            estado=EstadoMeta.activa if not goal_data.estado else EstadoMeta(goal_data.estado),
            id_usuario=user_id,
            id_grupo=goal_data.id_grupo
        )

        self.db.add(db_goal)
        self.db.commit()
        self.db.refresh(db_goal)
        return db_goal

    def get_goal_by_id(self, goal_id: int, user_id: int) -> Optional[Meta]:
        """Obtener meta por ID (del usuario o de un grupo al que pertenece)"""
        goal = self.db.query(Meta).filter(
            Meta.id_meta == goal_id
        ).first()
        
        if not goal:
            return None
        
        # Si es meta personal del usuario
        if goal.id_usuario == user_id and not goal.id_grupo:
            return goal
        
        # Si es meta de grupo, verificar que el usuario pertenece al grupo
        if goal.id_grupo:
            from app.models.user_group import UsuarioGrupo
            user_in_group = self.db.query(UsuarioGrupo).filter(
                UsuarioGrupo.id_usuario == user_id,
                UsuarioGrupo.id_grupo == goal.id_grupo
            ).first()
            if user_in_group:
                return goal
        
        return None

    def get_goals_by_user(self, user_id: int, skip: int = 0, limit: int = 100, personal_only: bool = False) -> List[Meta]:
        """Obtener todas las metas de un usuario (personales o todas incluyendo grupos)"""
        query = self.db.query(Meta).filter(
            Meta.id_usuario == user_id
        )
        
        if personal_only:
            query = query.filter(Meta.id_grupo.is_(None))
        
        return query.offset(skip).limit(limit).all()

    def get_goals_by_group(self, group_id: int, user_id: int, skip: int = 0, limit: int = 100) -> List[Meta]:
        """Obtener metas de un grupo (solo si el usuario pertenece al grupo)"""
        # Primero verificar que el usuario pertenece al grupo
        from app.models.user_group import UsuarioGrupo
        user_in_group = self.db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_usuario == user_id,
            UsuarioGrupo.id_grupo == group_id
        ).first()

        if not user_in_group:
            return []

        return self.db.query(Meta).filter(
            Meta.id_grupo == group_id
        ).offset(skip).limit(limit).all()

    def update_goal(self, goal_id: int, goal_data: MetaUpdate, user_id: int) -> Optional[Meta]:
        """Actualizar meta (del usuario o de un grupo al que pertenece)"""
        goal = self.get_goal_by_id(goal_id, user_id)
        if not goal:
            return None

        # Verificar que el grupo sea válido si se está actualizando
        if goal_data.id_grupo is not None:
            from app.models.user_group import UsuarioGrupo
            user_in_group = self.db.query(UsuarioGrupo).filter(
                UsuarioGrupo.id_usuario == user_id,
                UsuarioGrupo.id_grupo == goal_data.id_grupo
            ).first()
            if not user_in_group:
                return None

        update_data = goal_data.dict(exclude_unset=True)
        
        # Manejar el estado como enum
        if 'estado' in update_data and update_data['estado']:
            update_data['estado'] = EstadoMeta(update_data['estado'])
        
        for field, value in update_data.items():
            setattr(goal, field, value)

        self.db.commit()
        self.db.refresh(goal)
        return goal

    def delete_goal(self, goal_id: int, user_id: int) -> bool:
        """Eliminar meta (solo del usuario autenticado o admin del grupo)"""
        goal = self.get_goal_by_id(goal_id, user_id)
        if not goal:
            return False

        self.db.delete(goal)
        self.db.commit()
        return True

    def get_goal_progress(self, goal_id: int, user_id: int) -> Optional[dict]:
        """Obtener progreso de una meta"""
        goal = self.get_goal_by_id(goal_id, user_id)
        if not goal:
            return None
        
        # Calcular monto acumulado desde aportes
        from app.models.goal_contribution import AporteMeta
        from sqlalchemy import func
        
        total_aportes = self.db.query(func.sum(AporteMeta.monto)).filter(
            AporteMeta.id_meta == goal_id
        ).scalar()
        
        monto_acumulado = Decimal(str(total_aportes)) if total_aportes else Decimal('0.00')
        
        # Actualizar monto acumulado en la meta si es diferente
        if goal.monto_acumulado != monto_acumulado:
            goal.monto_acumulado = monto_acumulado
            # Verificar si se completó
            if monto_acumulado >= goal.monto_objetivo and goal.estado == EstadoMeta.activa:
                goal.estado = EstadoMeta.completada
            self.db.commit()
            self.db.refresh(goal)
        
        porcentaje = float((monto_acumulado / goal.monto_objetivo) * 100) if goal.monto_objetivo > 0 else 0.0
        
        return {
            "id_meta": goal.id_meta,
            "nombre": goal.nombre,
            "monto_objetivo": float(goal.monto_objetivo),
            "monto_acumulado": float(monto_acumulado),
            "porcentaje_completado": round(porcentaje, 2),
            "estado": goal.estado.value if goal.estado else None,
            "faltante": float(goal.monto_objetivo - monto_acumulado) if monto_acumulado < goal.monto_objetivo else 0.0
        }

    def get_goals_by_status(self, user_id: int, estado: str, personal_only: bool = False) -> List[Meta]:
        """Obtener metas por estado"""
        query = self.db.query(Meta).filter(
            Meta.id_usuario == user_id,
            Meta.estado == EstadoMeta(estado)
        )
        
        if personal_only:
            query = query.filter(Meta.id_grupo.is_(None))
        
        return query.all()

