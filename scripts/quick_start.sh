#!/bin/bash

# Script de Inicio Rápido - Sistema Tarifario CRA 720
# Este script configura y ejecuta todo el sistema con datos de prueba

set -e  # Salir si hay algún error

echo "=================================================="
echo "🚀 SISTEMA TARIFARIO - RESOLUCIÓN CRA 720 DE 2015"
echo "=================================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para mostrar pasos
step() {
    echo -e "${BLUE}📌 $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    error "Error: Debes ejecutar este script desde el directorio backend/"
    exit 1
fi

# 1. Instalar dependencias
step "Paso 1: Instalando dependencias de Python..."
pip install -r requirements.txt --quiet
success "Dependencias instaladas"

# 2. Verificar variables de entorno
step "Paso 2: Verificando configuración..."
if [ ! -f ".env" ]; then
    warning "Archivo .env no encontrado. Creando uno con valores por defecto..."
    cat > .env << EOF
DATABASE_URL=sqlite:///./sanitation.db
SECRET_KEY=your-secret-key-here-change-in-production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123456
EOF
    success "Archivo .env creado"
else
    success "Archivo .env encontrado"
fi

# 3. Ejecutar migraciones
step "Paso 3: Ejecutando migraciones de base de datos..."
alembic upgrade head 2>/dev/null || {
    warning "Alembic falló, intentando con SQLModel..."
    python -c "from app.db import init_db; init_db()"
}
success "Base de datos inicializada"

# 4. Generar datos de prueba
step "Paso 4: Generando datos de prueba..."
python scripts/generate_test_data.py
success "Datos de prueba generados"

echo ""
echo "=================================================="
echo "✅ SISTEMA CONFIGURADO Y LISTO"
echo "=================================================="
echo ""
echo -e "${GREEN}🚀 Para iniciar el servidor, ejecuta:${NC}"
echo -e "   ${BLUE}uvicorn app.main:app --reload${NC}"
echo ""
echo -e "${GREEN}📚 Una vez iniciado, accede a:${NC}"
echo -e "   • Documentación API: ${BLUE}http://localhost:8000/docs${NC}"
echo -e "   • Health Check: ${BLUE}http://localhost:8000/health${NC}"
echo ""
echo -e "${GREEN}🔑 Credenciales de acceso:${NC}"
echo -e "   • Usuario SYSTEM: ${BLUE}admin@system.com${NC} / ${BLUE}admin123${NC}"
echo -e "   • Admin Empresa 1: ${BLUE}admin@limpiezatotalcalisas.com${NC} / ${BLUE}admin123${NC}"
echo -e "   • Operador Empresa 1: ${BLUE}operador@limpiezatotalcalisas.com${NC} / ${BLUE}user123${NC}"
echo ""
echo -e "${GREEN}🧪 Para probar el cálculo de tarifas:${NC}"
echo -e "   1. Obtén un token JWT en ${BLUE}/auth/login${NC}"
echo -e "   2. Calcula tarifa: ${BLUE}POST /api/tariff/calculate${NC}"
echo -e "      ${YELLOW}Body: {\"aps_id\": 1, \"period\": \"2026-02\"}${NC}"
echo ""
echo "=================================================="
