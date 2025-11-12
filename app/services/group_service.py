"""
Servicio para gestión de grupos
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.group import Grupo
from app.models.user_group import UsuarioGrupo, RolGrupo
from app.schemas.group import GrupoCreate, GrupoUpdate


class GroupService:
    """Servicio para operaciones de grupos"""

    def __init__(self, db: Session):
        self.db = db

    def create_group(self, group_data: GrupoCreate, creator_id: int) -> Grupo:
        """Crear nuevo grupo y agregar al creador como admin"""
        db_group = Grupo(
            nombre=group_data.nombre,
            descripcion=group_data.descripcion,
            creado_por=creator_id
        )

        self.db.add(db_group)
        self.db.flush()  # Para obtener el id_grupo
        
        # Agregar al creador como admin del grupo
        usuario_grupo = UsuarioGrupo(
            id_usuario=creator_id,
            id_grupo=db_group.id_grupo,
            rol=RolGrupo.admin
        )
        self.db.add(usuario_grupo)
        self.db.commit()
        self.db.refresh(db_group)
        return db_group

    def get_group_by_id(self, group_id: int) -> Optional[Grupo]:
        """Obtener grupo por ID"""
        return self.db.query(Grupo).filter(Grupo.id_grupo == group_id).first()

    def get_user_groups(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Grupo]:
        """Obtener todos los grupos a los que pertenece un usuario"""
        return self.db.query(Grupo).join(UsuarioGrupo).filter(
            UsuarioGrupo.id_usuario == user_id
        ).offset(skip).limit(limit).all()

    def get_groups_created_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Grupo]:
        """Obtener grupos creados por un usuario"""
        return self.db.query(Grupo).filter(
            Grupo.creado_por == user_id
        ).offset(skip).limit(limit).all()

    def update_group(self, group_id: int, group_data: GrupoUpdate, user_id: int) -> Optional[Grupo]:
        """Actualizar grupo (solo el creador o admin puede actualizar)"""
        group = self.get_group_by_id(group_id)
        if not group:
            return None

        # Verificar permisos
        if not self._is_group_admin(group_id, user_id):
            return None

        update_data = group_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(group, field, value)

        self.db.commit()
        self.db.refresh(group)
        return group

    def delete_group(self, group_id: int, user_id: int) -> bool:
        """Eliminar grupo (solo el creador puede eliminar)"""
        group = self.get_group_by_id(group_id)
        if not group:
            return False

        # Solo el creador puede eliminar
        if group.creado_por != user_id:
            return False

        self.db.delete(group)
        self.db.commit()
        return True

    def is_user_in_group(self, group_id: int, user_id: int) -> bool:
        """Verificar si un usuario pertenece a un grupo"""
        return self.db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_grupo == group_id,
            UsuarioGrupo.id_usuario == user_id
        ).first() is not None

    def _is_group_admin(self, group_id: int, user_id: int) -> bool:
        """Verificar si un usuario es admin de un grupo"""
        usuario_grupo = self.db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_grupo == group_id,
            UsuarioGrupo.id_usuario == user_id
        ).first()
        
        if not usuario_grupo:
            return False
        
        return usuario_grupo.rol == RolGrupo.admin

    def add_user_to_group(self, group_id: int, user_id: int, rol: RolGrupo = RolGrupo.miembro) -> bool:
        """Agregar usuario a un grupo"""
        # Verificar que no esté ya en el grupo
        if self.is_user_in_group(group_id, user_id):
            return False

        usuario_grupo = UsuarioGrupo(
            id_usuario=user_id,
            id_grupo=group_id,
            rol=rol
        )
        self.db.add(usuario_grupo)
        self.db.commit()
        return True

    def remove_user_from_group(self, group_id: int, user_id: int, remover_id: int) -> bool:
        """Remover usuario de un grupo (solo admin o el mismo usuario)"""
        # Verificar permisos
        if not self._is_group_admin(group_id, remover_id) and user_id != remover_id:
            return False

        # El creador no puede ser removido
        group = self.get_group_by_id(group_id)
        if group and group.creado_por == user_id:
            return False

        usuario_grupo = self.db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_grupo == group_id,
            UsuarioGrupo.id_usuario == user_id
        ).first()

        if not usuario_grupo:
            return False

        self.db.delete(usuario_grupo)
        self.db.commit()
        return True

    def get_group_members(self, group_id: int) -> List[UsuarioGrupo]:
        """Obtener todos los miembros de un grupo"""
        return self.db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_grupo == group_id
        ).all()

    def change_member_role(self, group_id: int, user_id: int, new_rol: RolGrupo, admin_id: int) -> bool:
        """Cambiar el rol de un miembro (solo admin puede hacerlo)"""
        if not self._is_group_admin(group_id, admin_id):
            return False

        usuario_grupo = self.db.query(UsuarioGrupo).filter(
            UsuarioGrupo.id_grupo == group_id,
            UsuarioGrupo.id_usuario == user_id
        ).first()

        if not usuario_grupo:
            return False

        usuario_grupo.rol = new_rol
        self.db.commit()
        return True

