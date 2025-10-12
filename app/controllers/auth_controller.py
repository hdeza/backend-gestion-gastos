"""
Controlador para autenticación
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import Usuario
from app.schemas.user import UsuarioCreate, UsuarioResponse, ChangePassword
from app.schemas.auth import Token
from app.services.user_service import UserService
from app.services.auth_service import AuthService

router = APIRouter()

# Configuración OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    """Obtener usuario actual autenticado"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    email = verify_token(token, credentials_exception)
    user_service = UserService(db)
    user = user_service.get_user_by_email(email)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registrar un nuevo usuario en el sistema
    """
    user_service = UserService(db)
    try:
        db_user = user_service.create_user(user)
        return db_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Iniciar sesión y obtener token de acceso
    """
    user_service = UserService(db)
    auth_service = AuthService(user_service)
    
    try:
        token = auth_service.authenticate_and_create_token(form_data.username, form_data.password)
        return token
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=UsuarioResponse)
async def read_users_me(current_user: Usuario = Depends(get_current_user)):
    """
    Obtener información del usuario autenticado
    """
    return current_user

@router.get("/verify-token")
async def verify_token_endpoint(current_user: Usuario = Depends(get_current_user)):
    """
    Verificar si el token es válido
    """
    return {"valid": True, "user": current_user.nombre}

@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambiar contraseña del usuario autenticado
    """
    user_service = UserService(db)
    success = user_service.change_password(
        current_user.id_usuario, 
        password_data.old_password, 
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta"
        )
    
    return {"message": "Contraseña actualizada exitosamente"}
