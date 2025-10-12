"""
Servicio para autenticación
"""
from datetime import timedelta
from app.core.security import create_access_token
from app.core.config import settings
from app.services.user_service import UserService
from app.schemas.auth import Token

class AuthService:
    """Servicio para operaciones de autenticación"""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    def create_access_token_for_user(self, email: str) -> Token:
        """Crear token de acceso para usuario"""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": email}, 
            expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")
    
    def authenticate_and_create_token(self, email: str, password: str) -> Token:
        """Autenticar usuario y crear token"""
        user = self.user_service.authenticate_user(email, password)
        if not user:
            raise ValueError("Credenciales incorrectas")
        
        return self.create_access_token_for_user(email)
