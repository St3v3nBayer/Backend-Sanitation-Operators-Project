# 🚀 Sistema Tarifario - Resolución CRA 720 de 2015

Sistema completo para cálculo de tarifas del servicio público de aseo según la **Resolución CRA 720 de 2015** de Colombia.

## 📋 Características

✅ **Cumplimiento Normativo Total**
- Implementa todas las fórmulas de la Resolución 720 de 2015
- Referencias automáticas a artículos específicos
- Trazabilidad completa para auditorías

✅ **Gestión de APS** (Áreas de Prestación del Servicio)
- Múltiples APS por empresa
- Datos geográficos y operativos
- Cálculo automático de distancia efectiva

✅ **Cálculo Tarifario Completo**
- CFT (Costo Fijo Total)
- CVNA (Costo Variable No Aprovechable)
- VBA (Valor Base Aprovechamiento)
- Tarifas por estrato (1-6) y comercial
- Subsidios y contribuciones

✅ **Simulador Avanzado**
- Escenarios "¿Qué pasaría si...?"
- Comparación de cálculos
- Sin afectar datos oficiales

✅ **Datos Mensuales**
- Registro de datos operativos
- Promedios automáticos de 6 meses
- Validación y auditoría

## 🏗️ Arquitectura

```
Backend (FastAPI + SQLModel + PostgreSQL/SQLite)
├── Models
│   ├── APS (Área de Prestación)
│   ├── APSMonthlyData (Datos mensuales)
│   └── TariffCalculation (Resultados)
├── Services
│   ├── TariffCalculator720 (Motor de cálculo)
│   └── TariffCalculationService (Orquestador)
└── API Routes
    ├── /api/aps (Gestión APS)
    └── /api/tariff (Cálculos)

Frontend (Next.js 16 + TypeScript + Tailwind)
└── [En desarrollo]
```

## 🚀 Inicio Rápido

### Opción 1: Script Automático (Recomendado)

```bash
cd backend
./scripts/quick_start.sh
```

Este script:
1. ✅ Instala dependencias
2. ✅ Crea base de datos
3. ✅ Ejecuta migraciones
4. ✅ Genera datos de prueba (3 empresas, 4 APS, 6 meses de datos)

### Opción 2: Manual

```bash
# 1. Instalar dependencias
cd backend
pip install -r requirements.txt

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 3. Ejecutar migraciones
alembic upgrade head

# 4. Generar datos de prueba
python scripts/generate_test_data.py

# 5. Iniciar servidor
uvicorn app.main:app --reload
```

## 🔑 Credenciales de Prueba

Después de ejecutar el script de datos de prueba:

### Usuario SYSTEM (todos los permisos)
- Email: `admin@system.com`
- Password: `admin123`

### Empresa 1: Limpieza Total Cali
- **Admin**: `admin@limpiezatotalcalisas.com` / `admin123`
- **Operador**: `operador@limpiezatotalcalisas.com` / `user123`

### Empresa 2: Aseo y Recolección del Valle
- **Admin**: `admin@aseoyrecolecciondelvalle.com` / `admin123`
- **Operador**: `operador@aseoyrecolecciondelvalle.com` / `user123`

### Empresa 3: EcoLimpieza Pacífico
- **Admin**: `admin@ecolimpiezapacifico.com` / `admin123`
- **Operador**: `operador@ecolimpiezapacifico.com` / `user123`

## 📚 API Endpoints

### Autenticación
```bash
POST /auth/login
Body: {"username": "admin@system.com", "password": "admin123"}
Response: {"access_token": "...", "token_type": "bearer"}
```

### Gestión de APS
```bash
# Listar APS de una empresa
GET /api/aps/company/{company_id}
Headers: Authorization: Bearer {token}

# Crear APS
POST /api/aps/
Headers: Authorization: Bearer {token}
Body: {
  "company_id": 1,
  "name": "APS Norte",
  "code": "APS-NOR-001",
  "municipality": "Cali",
  "department": "Valle del Cauca",
  "distance_to_landfill_km": 25.3,
  ...
}

# Ver resumen de APS (incluye promedios)
GET /api/aps/{aps_id}/summary
Headers: Authorization: Bearer {token}
```

### Datos Mensuales
```bash
# Registrar datos del mes
POST /api/aps/{aps_id}/monthly-data
Headers: Authorization: Bearer {token}
Body: {
  "period": "2026-02",
  "num_subscribers_total": 12450,
  "tons_collected_non_recyclable": 850.5,
  "tons_received_landfill": 920.3,
  ...
}

# Ver promedios de 6 meses
GET /api/aps/{aps_id}/averages/2026-02
Headers: Authorization: Bearer {token}
```

### Cálculo de Tarifas
```bash
# Calcular tarifa oficial
POST /api/tariff/calculate
Headers: Authorization: Bearer {token}
Body: {
  "aps_id": 1,
  "period": "2026-02",
  "calculation_type": "official"
}

Response: {
  "id": 1,
  "cft": 8250.00,
  "cvna": 35890.00,
  "vba": 1710.00,
  "tariff_stratum_4_base": 45850.00,
  "breakdown": {
    "ccs": 1224.00,
    "clus": 3156.00,
    "cbls": 3870.00,
    "crt": 22345.00,
    "cdf": 11230.00,
    "ctl": 2315.00
  },
  "validations": {
    "alerts": [...]
  }
}

# Crear simulación
POST /api/tariff/simulate
Headers: Authorization: Bearer {token}
Body: {
  "aps_id": 1,
  "period": "2026-02",
  "is_simulation": true,
  "simulation_name": "Escenario +20% suscriptores",
  "simulation_data": {
    "num_subscribers_total": 15000
  }
}

# Comparar dos cálculos
POST /api/tariff/compare?calculation_id_1=1&calculation_id_2=2
Headers: Authorization: Bearer {token}

# Ver historial de cálculos
GET /api/tariff/aps/{aps_id}/history?only_official=true&limit=20
Headers: Authorization: Bearer {token}
```

## 📊 Datos de Prueba Generados

El script `generate_test_data.py` crea:

### 3 Empresas
1. **Limpieza Total Cali S.A.S.** - 2 APS en Cali (Segmento 1)
2. **Aseo y Recolección del Valle** - 1 APS en Palmira (Segmento 2)
3. **EcoLimpieza Pacífico** - 1 APS en Buenaventura (Segmento 2, costero)

### 4 APS (Áreas de Prestación)
Cada uno con:
- Datos geográficos completos
- Distancia al relleno sanitario
- Configuración de segmento
- Características especiales (costero, estación transferencia, etc.)

### 6 Meses de Datos Operativos
Para cada APS (septiembre 2025 - febrero 2026):
- Número de suscriptores por estrato
- Toneladas recolectadas por tipo
- Actividades de limpieza urbana
- Datos de disposición final
- Tratamiento de lixiviados
- Datos de flota vehicular

## 🧪 Ejemplos de Uso

### Caso 1: Calcular Tarifa Oficial

```bash
# 1. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@system.com","password":"admin123"}'

# 2. Calcular tarifa (usa el token del paso 1)
curl -X POST http://localhost:8000/api/tariff/calculate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "aps_id": 1,
    "period": "2026-02",
    "calculation_type": "official"
  }'
```

### Caso 2: Simular Escenario

```bash
curl -X POST http://localhost:8000/api/tariff/simulate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "aps_id": 1,
    "period": "2026-02",
    "is_simulation": true,
    "simulation_name": "Aumento 30% toneladas",
    "simulation_data": {
      "tons_collected_non_recyclable": 1100
    }
  }'
```

### Caso 3: Comparar Escenarios

```bash
curl -X POST "http://localhost:8000/api/tariff/compare?calculation_id_1=1&calculation_id_2=2" \
  -H "Authorization: Bearer {TOKEN}"
```

## 📖 Documentación API

Una vez iniciado el servidor, accede a:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔍 Validaciones Automáticas

El sistema genera alertas automáticas cuando detecta:
- ⚠️ Distancia > 50 km al relleno (considerar estación transferencia)
- ⚠️ Relleno < 2,400 ton/mes (aplica ajuste Art. 28)
- ⚠️ Flota > 12 años (descuento por antigüedad aplicado)
- ⚠️ Municipio costero (ajuste salinidad +1.97%)

## 📝 Referencias Normativas

Todas las fórmulas incluyen referencias automáticas a:
- Artículos específicos de la Resolución CRA 720 de 2015
- Anexos técnicos
- Parágrafos aplicables

## 🛠️ Desarrollo

### Estructura del Proyecto
```
backend/
├── app/
│   ├── models/         # Modelos SQLModel
│   ├── schemas/        # Schemas Pydantic
│   ├── services/       # Lógica de negocio
│   ├── controllers/    # Controladores
│   ├── repositories/   # Acceso a datos
│   └── routes/         # Endpoints API
├── scripts/
│   ├── generate_test_data.py
│   └── quick_start.sh
└── alembic/            # Migraciones
```

### Agregar Nuevas Funcionalidades

1. **Nuevo endpoint**: Crear en `app/routes/`
2. **Nueva lógica**: Agregar a `app/services/`
3. **Nuevo modelo**: Definir en `app/models/`
4. **Migración**: Usar Alembic para cambios de BD

## 🐛 Solución de Problemas

### Error: "No module named 'app'"
```bash
# Asegúrate de estar en el directorio backend/
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Error: "Database is locked"
```bash
# Si usas SQLite, cierra todas las conexiones
rm sanitation.db
python scripts/generate_test_data.py
```

### Error al generar datos de prueba
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

## 📞 Soporte

Para preguntas o problemas:
1. Revisa la documentación API en `/docs`
2. Verifica los logs del servidor
3. Consulta el documento `RESOLUCION_720_ANALISIS_FORMULA.md`

## 📄 Licencia

Privado - Uso interno de la empresa

---

**Versión**: 2.0.0  
**Última actualización**: Febrero 17, 2026
