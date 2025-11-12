"""
Configuración central de la aplicación
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Configuración de la aplicación
    APP_NAME: str = "Gestión de Gastos API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Configuración de base de datos
    DATABASE_URL: str = "postgresql://usuario:password@localhost:5432/gestion_gastos"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "gestion_gastos"
    DB_USER: str = "usuario"
    DB_PASSWORD: str = "password"
    
    # Configuración JWT
    SECRET_KEY: str = "tu_clave_secreta_muy_segura_aqui"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configuración CORS
    ALLOWED_ORIGINS: list = ["*"]
    
    # URL del frontend para links de invitación
    FRONTEND_URL: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()
