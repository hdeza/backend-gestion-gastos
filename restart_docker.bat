@echo off
REM Script para reiniciar Docker en Windows
REM Uso: restart_docker.bat

echo 🔄 Reiniciando contenedores Docker...

REM Detener y eliminar contenedores
echo ⏹️  Deteniendo contenedores...
docker-compose down

REM Reconstruir imágenes
echo 🔨 Reconstruyendo imágenes...
docker-compose build --no-cache

REM Iniciar contenedores
echo 🚀 Iniciando contenedores...
docker-compose up -d

REM Esperar a que los servicios estén listos
echo ⏳ Esperando a que los servicios estén listos...
timeout /t 5 /nobreak >nul

REM Verificar estado
echo 📊 Estado de los contenedores:
docker-compose ps

echo.
echo ✅ Docker reiniciado exitosamente
echo 🌐 API disponible en: http://localhost:8000
echo 📚 Documentación en: http://localhost:8000/docs
echo.
echo 💡 Para ver los logs: docker-compose logs -f api
echo 💡 Para ejecutar las pruebas: python test_groups_invitations.py

pause

