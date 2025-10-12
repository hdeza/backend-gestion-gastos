from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models import Usuario
from schemas import UsuarioCreate, UsuarioResponse, UsuarioLogin, Token
from auth import verify_password, get_password_hash, create_access_token, verify_token
from datetime import timedelta
import os

router = APIRouter()

# Configuración OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Función para obtener usuario actual
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    correo = verify_token(token, credentials_exception)
    user = db.query(Usuario).filter(Usuario.correo == correo).first()
    if user is None:
        raise credentials_exception
    return user

# Endpoint para registro de usuarios
@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registrar un nuevo usuario en el sistema
    """
    # Verificar si el usuario ya existe
    db_user = db.query(Usuario).filter(Usuario.correo == user.correo).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado"
        )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user.contrasena)
    db_user = Usuario(
        nombre=user.nombre,
        correo=user.correo,
        contrasena_hash=hashed_password,
        moneda_preferida=user.moneda_preferida
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

# Endpoint para login
@router.post("/login", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Iniciar sesión y obtener token de acceso
    """
    # Buscar usuario por correo
    user = db.query(Usuario).filter(Usuario.correo == form_data.username).first()
    
    # Verificar usuario y contraseña
    if not user or not verify_password(form_data.password, user.contrasena_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")))
    access_token = create_access_token(
        data={"sub": user.correo}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint para obtener perfil del usuario actual
@router.get("/me", response_model=UsuarioResponse)
async def read_users_me(current_user: Usuario = Depends(get_current_user)):
    """
    Obtener información del usuario autenticado
    """
    return current_user

# Endpoint para verificar token
@router.get("/verify-token")
async def verify_token_endpoint(current_user: Usuario = Depends(get_current_user)):
    """
    Verificar si el token es válido
    """
    return {"valid": True, "user": current_user.nombre}

# Endpoint para cambiar contraseña
@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambiar contraseña del usuario autenticado
    """
    # Verificar contraseña actual
    if not verify_password(old_password, current_user.contrasena_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta"
        )
    
    # Actualizar contraseña
    current_user.contrasena_hash = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Contraseña actualizada exitosamente"}
