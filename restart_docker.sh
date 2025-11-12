#!/bin/bash

# Script para reiniciar Docker y cargar todos los cambios
# Uso: ./restart_docker.sh

echo "🔄 Reiniciando contenedores Docker..."

# Detener y eliminar contenedores
echo "⏹️  Deteniendo contenedores..."
docker-compose down

# Eliminar volúmenes (opcional, descomentar si quieres limpiar la BD)
# echo "🗑️  Eliminando volúmenes..."
# docker-compose down -v

# Reconstruir imágenes
echo "🔨 Reconstruyendo imágenes..."
docker-compose build --no-cache

# Iniciar contenedores
echo "🚀 Iniciando contenedores..."
docker-compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 5

# Verificar estado
echo "📊 Estado de los contenedores:"
docker-compose ps

echo ""
echo "✅ Docker reiniciado exitosamente"
echo "🌐 API disponible en: http://localhost:8000"
echo "📚 Documentación en: http://localhost:8000/docs"
echo ""
echo "💡 Para ver los logs: docker-compose logs -f api"
echo "💡 Para ejecutar las pruebas: python3 test_groups_invitations.py"

