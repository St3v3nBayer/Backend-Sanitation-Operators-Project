# 📋 ANÁLISIS COMPLETO - RESOLUCIÓN 720 DE 2015
## Fórmula Tarifaria para Servicio Público de Aseo

**Fecha de análisis:** 17 de Febrero, 2026  
**Documento base:** Resolución CRA 720 de 2015

---

## 🎯 RESUMEN EJECUTIVO

La Resolución 720 de 2015 establece una metodología tarifaria compleja para el servicio público de aseo en Colombia. El sistema calcula tarifas basadas en:

1. **Costos Fijos** por suscriptor
2. **Costos Variables** por tonelada de residuos
3. **Diferentes actividades** del servicio de aseo

---

## 📊 ESTRUCTURA GENERAL DE LA TARIFA

### Artículo 39 - Tarifa Final por Suscriptor

La tarifa final se compone de DOS casos:

#### **CASO 1: Usuario SIN aforo (la mayoría)**

```
TFS_u,z = (CFT + CVNA × (TRBL + TRLU + TRNA_u,z + TRRA) + (VBA × TRA)) × (1 ± FCS_u)
```

#### **CASO 2: Usuario CON aforo (grandes productores)**

```
TFS_i,z = (CFT + CVNA × (TRBL + TRLU + TAFNA_i,z + TRRA) + (VBA × TAFA_i,k)) × (1 ± FCS_u)
```

---

## 🧩 COMPONENTES DE LA FÓRMULA

### 1. COSTO FIJO TOTAL (CFT) - Artículo 11

```
CFT = CCS + CLUS + CBLS
```

**Donde:**
- `CCS` = Costo de Comercialización por Suscriptor
- `CLUS` = Costo de Limpieza Urbana por Suscriptor  
- `CBLS` = Costo de Barrido y Limpieza por Suscriptor

---

### 1.1 Costo de Comercialización (CCS) - Artículo 14

**Valores máximos a precios de diciembre 2014:**

| Segmento | Facturación con Acueducto | Facturación con Energía |
|----------|---------------------------|-------------------------|
| 1 (>100K suscriptores) | $1,223.39 | $1,829.86 |
| 2 (5K-100K suscriptores) | $1,368.85 | $1,975.31 |

**IMPORTANTE:** Si existe actividad de aprovechamiento, el CCS se incrementa en 30%.

---

### 1.2 Costo de Limpieza Urbana (CLUS) - Artículo 15

```
CLUS = Σ(CP_j + CCC × mCC_j² + CLAV × mLAV_j² + CLP × kLP_j + (CCEI × TI_j + CCEM × TM_j)) / N
```

**Componentes:**

| Actividad | Costo Máximo (dic 2014) | Unidad |
|-----------|-------------------------|--------|
| **Poda de árboles (CP)** | Promedio de 6 meses | $/mes |
| **Corte de césped (CCC)** | $57 (Seg 1), $86 (Seg 2) | $/m² |
| **Lavado de áreas (CLAV)** | $166 + 5.56 × ($/m³ agua / 1000) | $/m² |
| **Limpieza de playas (CLP)** | $10,789 | $/km |
| **Instalación cestas (CCEI)** | $6,276 | $/cesta-mes |
| **Mantenimiento cestas (CCEM)** | $571 | $/cesta-mes |

---

### 1.3 Costo de Barrido y Limpieza (CBLS) - Artículo 21

```
CBLS = Σ(CBL_j × LBL_j) / N
```

**Donde:**
- `CBL_j` = $28,985 por kilómetro barrido (máximo, dic 2014)
- `LBL_j` = Longitud de vías barridas (km/mes, promedio 6 meses)
- `N` = Número promedio de suscriptores totales

**Conversión áreas a kilómetros:** `m² × 0.002 km/m²`

---

## 2. COSTO VARIABLE NO APROVECHABLE (CVNA) - Artículo 12

```
CVNA = CRT + CDF + CTL
```

---

### 2.1 Costo de Recolección y Transporte (CRT) - Artículo 24

```
CRT_z = MIN(f1, f2) + PRT_z
```

**Función 1 (Compactador directo al relleno):**
```
f1 = 64,745 + 738 × D + 8,683,846 / QRT_z
```

**Función 2 (Con estación de transferencia):**
```
f2 = 87,823 + 278 × D + 25,211,213 / QRT_z
```

**Variables:**
- `D` = Distancia del centroide al sitio de disposición final (km)
  - 1 km vía sin pavimentar = 1.25 km vía pavimentada
- `QRT_z` = Promedio toneladas recolectadas/mes (6 meses)
- `PRT_z` = Peajes ida y vuelta

**Ajustes especiales:**
- **Municipios costeros (Tabla 3, Anexo I):** Incremento 1.97% (salinidad)
- **Antigüedad de vehículos:** Descuento 2% por cada año que supere:
  - 12 años (1 turno diario)
  - 6 años (2+ turnos diarios)

---

### 2.2 Costo de Disposición Final (CDF) - Artículo 28

```
CDF = CDF_VU + CDF_PC
```

**Vida Útil (20 años):**
```
CDF_VU = MIN(18,722 + 132,924,379 / QRS, 139,896)
```

**Post-Clausura (10 años):**
```
CDF_PC = MIN(242 + 11,652,352 / QRS, 6,185)
```

**Variables:**
- `QRS` = Promedio mensual residuos recibidos en relleno (6 meses)

**Ajustes:**
- **Rellenos <2,400 ton/mes con altura <9m:** Incremento hasta 10%
- **Post-clausura >10 años:** Factor k = 0.8211 × ln(10 + ΔT) - 0.8954

---

### 2.3 Costo de Tratamiento de Lixiviados (CTL) - Artículo 32

```
CTL = (CTLM × VL) + CMTLX) / QRS
```

```
CTLM = CTLM_VU + CTLM_PC
```

**4 Escenarios según objetivo de calidad (Anexo II):**

| Escenario | Remoción | Vida Útil (VU) | Post-Clausura (PC) |
|-----------|----------|----------------|---------------------|
| 1 | SS + MO | MIN(8,139; 898 + 44,781,608/VL) | MIN(1,074; 102 + 5,875,125/VL) × k |
| 2 | SS + MO + N | MIN(14,918; 1,740 + 82,290,106/VL) | MIN(1,628; 167 + 8,930,368/VL) × k |
| 3 | SS + MO + SI + CO | MIN(18,787; 2,212 + 103,676,696/VL) | MIN(2,104; 225 + 11,561,342/VL) × k |
| 4 | SS + MO + N + SI + CO | MIN(21,820; 2,554 + 120,381,714/VL) | MIN(2,488; 261 + 13,658,195/VL) × k |
| 5 | Solo Recirculación | $2,348 por m³ | N/A |

**Variables:**
- `VL` = Volumen promedio lixiviados tratados (m³/mes, 6 meses)
- `CMTLX` = Costo tasa ambiental ($/m³)
- `k` = Factor post-clausura extendida: 0.8415 × ln(10 + ΔT) - 0.9429

---

## 3. VALOR BASE DE APROVECHAMIENTO (VBA) - Artículo 34

```
VBA = (CRT_p + CDF_p) × (1 - DINC)
```

**Donde:**
```
CRT_p = Σ(CRT_j × QRT_j) / Σ(QRT_j)
CDF_p = Σ(CDF_j × QRS_j) / Σ(QRS_j)
```

- `DINC` = Descuento incentivo separación en la fuente (hasta 4%)

---

## 4. TONELADAS POR SUSCRIPTOR

### 4.1 Toneladas Comunes (Artículo 40)

Calculadas mensualmente por todos los prestadores del municipio:

```
TRBL = Promedio[Σ QBL_j] / N
TRLU = Promedio[Σ QLU_j] / N  
TRRA = Promedio[Σ QR_j] / (N - ND)
TRA = Promedio[Σ QA_j] / (N - ND - NA)
```

**Donde:**
- `QBL_j` = Toneladas barrido y limpieza
- `QLU_j` = Toneladas limpieza urbana
- `QR_j` = Toneladas rechazo aprovechamiento (medidas en ECA)
- `QA_j` = Toneladas efectivamente aprovechadas (medidas en ECA)
- `N` = Suscriptores totales (promedio 6 meses)
- `ND` = Suscriptores desocupados
- `NA` = Suscriptores grandes productores con aforo

---

### 4.2 Toneladas No Aprovechables (TRNA) - Artículo 41

**Para usuarios SIN aforo:**

```
TRNA_u,z = ((QNA_z - QR_z - Σ TAFNA_i,z) × F_u) / Σ((n_u,z - na_u,z - nD_u,z) × F_u)
```

**Factores de Producción (F_u) - Artículo 42:**

| Tipo Usuario | Factor F | Descripción |
|--------------|----------|-------------|
| F1 | 0.79 | Estrato 1 residencial |
| F2 | 0.86 | Estrato 2 residencial |
| F3 | 0.90 | Estrato 3 residencial |
| F4 | 1.00 | Estrato 4 residencial |
| F5 | 1.22 | Estrato 5 residencial |
| F6 | 1.50 | Estrato 6 residencial |
| F7 | 2.44 | Pequeño productor no residencial |
| F8 | 0.00 | Inmueble desocupado |

---

## 5. SUBSIDIOS Y CONTRIBUCIONES (FCS_u)

Factor aplicado al final según estrato:
- **Subsidio:** Signo negativo (-)
- **Contribución:** Signo positivo (+)

Establecidos por la entidad territorial según normativa vigente.

---

## 🏢 ZONAS Y ÁREAS DE PRESTACIÓN DEL SERVICIO (APS)

### Definición (Artículo 4)

**APS (Área de Prestación del Servicio):** Área geográfica del municipio/distrito donde el prestador de recolección y transporte de residuos no aprovechables presta el servicio.

### Cálculo del Centroide (Artículo 9)

El centroide es el punto que representa donde se concentra la producción de residuos del APS:

**Metodología:**
1. Dividir plano del APS en áreas homogéneas (máx 1 km²)
2. Establecer centroide particular por área (baricentro)
3. Calcular promedio ponderado de coordenadas por:
   - Número de suscriptores, O
   - Producción de residuos

**Alternativa:** Calcular distancia desde límite del APS más cercano al sitio de disposición final.

### Aplicación en Tarifas

Cada APS `z` tiene su propia tarifa porque:
- Distancia `D` al relleno puede variar
- Cantidad de residuos `QNA_z` puede ser diferente
- Número de suscriptores `n_u,z` varía por APS

---

## 📍 CASOS DE USO DE ZONAS/APS

### Escenario 1: Ciudad con un solo prestador
- **1 APS** = Todo el perímetro urbano
- **1 centroide** para toda la ciudad
- **1 distancia D** al relleno
- **Tarifa uniforme** para todos (ajustada por estrato)

### Escenario 2: Ciudad con múltiples prestadores
- **Múltiples APS** (una por prestador)
- **Múltiples centroides**
- **Diferentes distancias D**
- **Tarifas diferentes** según APS

### Escenario 3: Prestador con varias APS en un municipio
- Calcula `CRT` promedio ponderado (Parágrafo 7, Art. 24)
- Aplica la misma tarifa a todas sus APS

---

## 💡 RESPUESTAS A TUS PREGUNTAS SOBRE ZONAS

### ¿Qué representa una zona en tu modelo de negocio?

**Según la Resolución 720:**
- **NO usa el término "zona" para tarifas**
- Usa **"APS" (Área de Prestación del Servicio)**
- El APS es el área geográfica donde opera UN prestador específico

**En tu sistema SaaS:**
- **"Zona"** puede ser sinónimo de **APS**
- Cada empresa de limpieza (usuario ADMIN) tendrá una o más APS
- Cada APS tiene su propio cálculo tarifario

### ¿Las tarifas varían por zona/APS?

**SÍ, varían por:**
1. **Distancia D** al sitio de disposición final
2. **Cantidad de toneladas** recolectadas `QRT_z`
3. **Número de suscriptores** `n_z`
4. **Costos específicos** de cada prestador

### ¿Una propiedad puede estar en múltiples zonas?

**NO.** Según Artículo 6:
- Cada suscriptor pertenece a **una sola APS**
- El CCU (Contrato de Condiciones Uniformes) especifica el APS del suscriptor

---

## 🗃️ MODELO DE DATOS PROPUESTO

### Tablas Principales

```python
class Company(SQLModel, table=True):
    """Empresa de limpieza (usuario ADMIN)"""
    id: int
    name: str
    nit: str
    # ... resto de campos

class APS(SQLModel, table=True):
    """Área de Prestación del Servicio"""
    id: int
    company_id: int  # FK a Company
    name: str  # Ej: "APS Norte de Cali"
    municipality: str
    
    # Datos geográficos
    centroid_lat: float
    centroid_lon: float
    distance_to_landfill_km: float  # D
    
    # Datos operativos
    num_subscribers: int  # N
    avg_tons_collected_month: float  # QRT_z
    
    created_at: datetime

class User(SQLModel, table=True):
    """Usuario final (suscriptor)"""
    id: int
    company_id: int  # FK a Company
    aps_id: int  # FK a APS (cada usuario en una sola APS)
    
    # Datos del suscriptor
    name: str
    address: str
    stratum: int  # 1-6 para residencial
    user_type: str  # "residential", "commercial", "industrial"
    
    # Datos de facturación
    has_weighing: bool  # ¿Tiene aforo?
    weighing_tons_month: float  # TAFNA_i,z (si tiene aforo)

class TariffCalculation(SQLModel, table=True):
    """Cálculo de tarifa para un período"""
    id: int
    company_id: int
    aps_id: int
    calculation_date: datetime
    period: str  # "2026-01"
    
    # Costos fijos
    cft: float  # Costo Fijo Total
    ccs: float  # Comercialización
    clus: float  # Limpieza Urbana
    cbls: float  # Barrido y Limpieza
    
    # Costos variables
    cvna: float  # Costo Variable No Aprovechable
    crt: float  # Recolección y Transporte
    cdf: float  # Disposición Final
    ctl: float  # Tratamiento Lixiviados
    
    # Aprovechamiento
    vba: float  # Valor Base Aprovechamiento
    
    # Toneladas promedio
    trbl: float  # Ton barrido/limpieza por suscriptor
    trlu: float  # Ton limpieza urbana por suscriptor
    trra: float  # Ton rechazo aprovechamiento por suscriptor
    tra: float  # Ton aprovechadas por suscriptor
```

---

## 🔧 VARIABLES QUE NECESITA INGRESAR EL USUARIO

### Para cada APS (Área de Prestación del Servicio):

#### **1. Datos Geográficos**
- Ubicación del centroide (lat, lon)
- Distancia al relleno sanitario (km)
- % vías sin pavimentar (para ajustar distancia)

#### **2. Datos Operativos Mensuales** (promedio 6 meses)
- Número de suscriptores totales
- Número de suscriptores desocupados
- Toneladas recolectadas no aprovechables
- Toneladas de barrido y limpieza
- Toneladas de limpieza urbana
- Toneladas de rechazo aprovechamiento
- Toneladas efectivamente aprovechadas

#### **3. Costos Específicos de Limpieza Urbana**
- Costo poda de árboles (promedio 6 meses)
- Metros² césped cortado
- Metros² áreas lavadas
- Kilómetros playas limpias
- Número cestas instaladas
- Número cestas con mantenimiento

#### **4. Datos de Disposición Final**
- Toneladas recibidas en relleno (promedio 6 meses)
- Volumen lixiviados tratados m³ (promedio 6 meses)
- Escenario de tratamiento (1-5)
- Costo tasa ambiental por m³

#### **5. Datos de Facturación**
- Tipo de facturación (acueducto o energía)
- Segmento (1 o 2)
- Municipio costero (sí/no)

#### **6. Datos de Vehículos** (para descuentos)
- Número de turnos diarios (1 o 2+)
- Antigüedad promedio flota (años)

---

## ⚙️ FLUJO DE CÁLCULO EN EL SISTEMA

### Paso 1: Configuración Inicial (Usuario ADMIN)
```
1. Crear Company
2. Crear APS(s) asociadas
3. Configurar datos geográficos del APS
4. Configurar datos operativos base
```

### Paso 2: Ingreso de Datos Mensuales
```
1. Ingresar toneladas del mes
2. Ingresar actividades CLUS del mes
3. Ingresar datos de lixiviados
4. Sistema calcula promedios de 6 meses
```

### Paso 3: Cálculo de Costos
```
1. Calcular CCS según segmento y tipo facturación
2. Calcular CLUS según actividades realizadas
3. Calcular CBLS según km barridos
4. Calcular CRT según función MIN(f1, f2)
5. Calcular CDF según toneladas recibidas
6. Calcular CTL según escenario de tratamiento
7. Calcular VBA según CRT y CDF promedio
```

### Paso 4: Cálculo de Toneladas por Suscriptor
```
1. Calcular TRBL, TRLU, TRRA, TRA (comunes a todos)
2. Calcular TRNA_u,z según factor de producción
```

### Paso 5: Cálculo de Tarifa Final
```
Para cada usuario:
  Si tiene aforo:
    TFS = (CFT + CVNA × (TRBL + TRLU + TAFNA + TRRA) + (VBA × TAFA)) × (1 ± FCS)
  Si NO tiene aforo:
    TFS = (CFT + CVNA × (TRBL + TRLU + TRNA + TRRA) + (VBA × TRA)) × (1 ± FCS)
```

---

## 🎯 RECOMENDACIONES PARA IMPLEMENTACIÓN

### 1. Estructura de Módulos

```
📦 backend/app/
├── models/
│   ├── company.py (existente)
│   ├── user.py (existente)
│   ├── aps.py (NUEVO - Área Prestación Servicio)
│   ├── tariff.py (existente - AMPLIAR)
│   ├── monthly_data.py (NUEVO - Datos mensuales)
│   └── tariff_calculation.py (NUEVO - Resultados cálculo)
├── services/
│   ├── tariff_calculator.py (NUEVO - Motor de cálculo)
│   ├── cost_calculator.py (NUEVO - Cálculo de costos)
│   └── tonnage_calculator.py (NUEVO - Cálculo toneladas)
└── controllers/
    ├── aps_controller.py (NUEVO)
    └── tariff_controller.py (existente - AMPLIAR)
```

### 2. Formularios de Entrada

**Formulario 1: Configuración APS**
- Datos geográficos
- Datos de sitio disposición final
- Configuración inicial

**Formulario 2: Datos Mensuales Operativos**
- Toneladas por actividad
- Número de suscriptores
- Actividades CLUS realizadas

**Formulario 3: Calculadora de Tarifa**
- Selección APS
- Período de cálculo
- Vista de resultados detallados

### 3. Simplificaciones Recomendadas para MVP

Para la primera versión, puedes:

1. **Usar valores predeterminados** para costos máximos (de la resolución)
2. **Un solo APS por empresa** inicialmente
3. **Factores de producción fijos** (Tabla de Art. 42)
4. **Escenario 2 de lixiviados** como predeterminado
5. **Segmento 2** como predeterminado

Luego, en versiones futuras, permitir personalización completa.

---

## 🚦 PRÓXIMOS PASOS

### Implementación Inmediata

1. **Crear modelo APS**
   - Tabla en base de datos
   - CRUD básico
   - Relación con Company

2. **Crear servicio TariffCalculator**
   - Implementar fórmulas de la Resolución 720
   - Separar cálculo por componentes (CFT, CVNA, VBA)
   - Validaciones de datos

3. **Actualizar modelo Tariff existente**
   - Agregar campos específicos de la Resolución 720
   - Quitar sistema genérico de fórmulas
   - Usar fórmulas específicas de la normativa

4. **Crear endpoints API**
   - POST /aps (crear área)
   - POST /aps/{id}/monthly-data (ingresar datos mes)
   - POST /aps/{id}/calculate-tariff (calcular tarifa)
   - GET /aps/{id}/tariff-breakdown (detalle cálculo)

### Testing

1. **Casos de prueba**
   - Municipio pequeño (Segmento 2, <10K suscriptores)
   - Municipio grande (Segmento 1, >100K suscriptores)
   - Con y sin aprovechamiento
   - Con y sin aforo

---

## 📚 REFERENCIAS

- **Resolución CRA 720 de 2015** - Comisión de Regulación de Agua Potable y Saneamiento Básico
- **Decreto 1077 de 2015** - Decreto Único Reglamentario del Sector Vivienda, Ciudad y Territorio
- **Ley 142 de 1994** - Régimen de Servicios Públicos Domiciliarios

---

## ✅ CONCLUSIÓN

La Resolución 720 de 2015 proporciona una metodología tarifaria **completa y detallada**. El concepto de **"zona"** en tu sistema debe entenderse como **"APS" (Área de Prestación del Servicio)**.

**Puntos clave:**
1. Cada empresa tiene una o más APS
2. Cada APS tiene su propia tarifa calculada
3. La tarifa varía por distancia, toneladas y número de suscriptores
4. Múltiples actividades contribuyen al costo final

**El sistema es complejo pero bien estructurado** - podemos implementarlo paso a paso, empezando con una versión simplificada y agregando complejidad gradualmente.
