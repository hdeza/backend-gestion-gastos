"""
Servicio para gestión de usuarios
"""
from sqlalchemy.orm import Session
from app.models.user import Usuario
from app.schemas.user import UsuarioCreate, UsuarioUpdate
from app.core.security import get_password_hash, verify_password
from typing import Optional

class UserService:
    """Servicio para operaciones de usuario"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UsuarioCreate) -> Usuario:
        """Crear nuevo usuario"""
        # Verificar si el usuario ya existe
        existing_user = self.db.query(Usuario).filter(Usuario.correo == user_data.correo).first()
        if existing_user:
            raise ValueError("El correo electrónico ya está registrado")
        
        # Crear nuevo usuario
        hashed_password = get_password_hash(user_data.contrasena)
        db_user = Usuario(
            nombre=user_data.nombre,
            correo=user_data.correo,
            contrasena_hash=hashed_password,
            moneda_preferida=user_data.moneda_preferida
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_user_by_email(self, email: str) -> Optional[Usuario]:
        """Obtener usuario por email"""
        return self.db.query(Usuario).filter(Usuario.correo == email).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[Usuario]:
        """Obtener usuario por ID"""
        return self.db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    
    def authenticate_user(self, email: str, password: str) -> Optional[Usuario]:
        """Autenticar usuario"""
        user = self.get_user_by_email(email)
        if not user or not verify_password(password, user.contrasena_hash):
            return None
        return user
    
    def update_user(self, user_id: int, user_data: UsuarioUpdate) -> Optional[Usuario]:
        """Actualizar usuario"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Cambiar contraseña del usuario"""
        user = self.get_user_by_id(user_id)
        if not user or not verify_password(old_password, user.contrasena_hash):
            return False
        
        user.contrasena_hash = get_password_hash(new_password)
        self.db.commit()
        return True
