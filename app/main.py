"""
Aplicación principal FastAPI con arquitectura MVC
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.core.config import settings
from app.controllers import auth_controller, user_controller

# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="API para sistema de gestión financiera para estudiantes universitarios",
    version=settings.APP_VERSION
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas en la base de datos
@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

# Incluir controladores (routers)
app.include_router(auth_controller.router, prefix="/api/auth", tags=["autenticación"])
app.include_router(user_controller.router, prefix="/api/users", tags=["usuarios"])

@app.get("/")
async def root():
    return {
        "message": "API de Gestión de Gastos - Sistema para estudiantes universitarios",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "API funcionando correctamente",
        "version": settings.APP_VERSION
    }
