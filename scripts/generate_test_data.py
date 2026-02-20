"""
Script para generar datos de prueba realistas
Crea empresas, APS, usuarios y datos mensuales de ejemplo
"""

import random
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine
from app.core.config import settings
from app.models.company import Company
from app.models.user import User
from app.models.aps import APS
from app.models.aps_monthly_data import APSMonthlyData
from app.core.security import get_password_hash


def generate_test_data(session: Session):
    """Genera datos de prueba completos"""
    
    print("🚀 Generando datos de prueba...")
    
    # ========================================
    # 1. CREAR EMPRESAS
    # ========================================
    print("\n📦 Creando empresas...")
    
    companies = [
        Company(
            name="Limpieza Total Cali S.A.S.",
            tax_id="900123456-1",
            address="Calle 5 # 40-30, Cali, Valle del Cauca",
            phone="+57 2 3334444",
            email="contacto@limpiezatotal.com.co",
            is_active=True
        ),
        Company(
            name="Aseo y Recolección del Valle",
            tax_id="900234567-2",
            address="Carrera 10 # 15-20, Palmira, Valle del Cauca",
            phone="+57 2 2221111",
            email="info@aseovalle.com.co",
            is_active=True
        ),
        Company(
            name="EcoLimpieza Pacífico",
            tax_id="900345678-3",
            address="Avenida Simón Bolívar # 25-50, Buenaventura, Valle del Cauca",
            phone="+57 2 2445566",
            email="servicios@ecopacifico.com.co",
            is_active=True
        )
    ]
    
    for company in companies:
        session.add(company)
    
    session.commit()
    
    for company in companies:
        session.refresh(company)
        print(f"  ✅ {company.name} (ID: {company.id})")
    
    # ========================================
    # 2. CREAR USUARIOS
    # ========================================
    print("\n👥 Creando usuarios...")
    
    # Usuario SYSTEM
    system_user = User(
        email="admin@system.com",
        username="system_admin",
        full_name="Administrador del Sistema",
        hashed_password=get_password_hash("admin123"),
        role="SYSTEM",
        company_id=None,
        is_active=True
    )
    session.add(system_user)
    
    # Usuarios por empresa
    users = []
    
    for company in companies:
        # ADMIN de la empresa
        admin = User(
            email=f"admin@{company.name.lower().replace(' ', '').replace('.', '')[:20]}.com",
            username=f"admin_{company.id}",
            full_name=f"Administrador {company.name}",
            hashed_password=get_password_hash("admin123"),
            role="ADMIN",
            company_id=company.id,
            is_active=True
        )
        users.append(admin)
        
        # USER operador
        user = User(
            email=f"operador@{company.name.lower().replace(' ', '').replace('.', '')[:20]}.com",
            username=f"user_{company.id}",
            full_name=f"Operador {company.name}",
            hashed_password=get_password_hash("user123"),
            role="USER",
            company_id=company.id,
            is_active=True
        )
        users.append(user)
    
    for user in users:
        session.add(user)
    
    session.commit()
    
    print(f"  ✅ Usuario SYSTEM: {system_user.email}")
    for user in users:
        print(f"  ✅ {user.role}: {user.email} (Empresa: {user.company_id})")
    
    # ========================================
    # 3. CREAR APS
    # ========================================
    print("\n📍 Creando Áreas de Prestación del Servicio (APS)...")
    
    aps_list = [
        # Empresa 1: Limpieza Total Cali - 2 APS
        APS(
            company_id=companies[0].id,
            name="APS Norte Cali",
            code="CALI-NOR-001",
            municipality="Cali",
            department="Valle del Cauca",
            centroid_lat=3.4516,
            centroid_lon=-76.5320,
            distance_to_landfill_km=18.5,
            unpaved_road_percentage=5.0,
            landfill_name="Relleno Sanitario Navarro",
            landfill_location="Cali, Valle del Cauca",
            uses_transfer_station=False,
            segment=1,  # >100K suscriptores
            is_coastal_municipality=False,
            billing_type="acueducto",
            is_active=True
        ),
        APS(
            company_id=companies[0].id,
            name="APS Sur Cali",
            code="CALI-SUR-001",
            municipality="Cali",
            department="Valle del Cauca",
            centroid_lat=3.3950,
            centroid_lon=-76.5197,
            distance_to_landfill_km=22.3,
            unpaved_road_percentage=8.0,
            landfill_name="Relleno Sanitario Navarro",
            landfill_location="Cali, Valle del Cauca",
            uses_transfer_station=False,
            segment=1,
            is_coastal_municipality=False,
            billing_type="acueducto",
            is_active=True
        ),
        
        # Empresa 2: Aseo Valle - 1 APS
        APS(
            company_id=companies[1].id,
            name="APS Palmira Centro",
            code="PALM-CEN-001",
            municipality="Palmira",
            department="Valle del Cauca",
            centroid_lat=3.5394,
            centroid_lon=-76.3036,
            distance_to_landfill_km=12.8,
            unpaved_road_percentage=15.0,
            landfill_name="Relleno Sanitario Regional",
            landfill_location="Palmira, Valle del Cauca",
            uses_transfer_station=False,
            segment=2,  # 5K-100K suscriptores
            is_coastal_municipality=False,
            billing_type="energia",
            is_active=True
        ),
        
        # Empresa 3: EcoLimpieza Pacífico - 1 APS
        APS(
            company_id=companies[2].id,
            name="APS Buenaventura",
            code="BUEN-TOT-001",
            municipality="Buenaventura",
            department="Valle del Cauca",
            centroid_lat=3.8801,
            centroid_lon=-77.0318,
            distance_to_landfill_km=28.7,
            unpaved_road_percentage=25.0,
            landfill_name="Relleno Sanitario El Papayo",
            landfill_location="Buenaventura, Valle del Cauca",
            uses_transfer_station=True,
            transfer_station_distance_km=15.0,
            segment=2,
            is_coastal_municipality=True,  # ¡Municipio costero! (ajuste 1.97%)
            billing_type="acueducto",
            is_active=True
        )
    ]
    
    for aps in aps_list:
        session.add(aps)
    
    session.commit()
    
    for aps in aps_list:
        session.refresh(aps)
        print(f"  ✅ {aps.name} - {aps.municipality}")
        print(f"     Código: {aps.code}")
        print(f"     Distancia efectiva: {aps.get_effective_distance()} km")
        print(f"     Segmento: {aps.segment}")
        if aps.is_coastal_municipality:
            print(f"     🌊 Municipio costero (ajuste salinidad +1.97%)")
    
    # ========================================
    # 4. CREAR DATOS MENSUALES (6 MESES)
    # ========================================
    print("\n📊 Creando datos mensuales (últimos 6 meses)...")
    
    # Fecha base: hace 6 meses
    end_date = datetime.now()
    
    for aps in aps_list:
        print(f"\n  📍 {aps.name}:")
        
        # Determinar rango base según segmento y ciudad
        if aps.segment == 1:  # Cali - gran ciudad
            base_subscribers = random.randint(100000, 150000)
            base_tons = random.randint(8000, 12000)
        else:  # Ciudades menores
            base_subscribers = random.randint(15000, 30000)
            base_tons = random.randint(1200, 2500)
        
        # Generar 6 meses de datos
        for month_offset in range(6):
            period_date = end_date - timedelta(days=30 * (5 - month_offset))
            period = period_date.strftime("%Y-%m")
            year = period_date.year
            month = period_date.month
            
            # Variación mensual realista (±5%)
            subscribers = int(base_subscribers * random.uniform(0.95, 1.05))
            tons_non_recyclable = base_tons * random.uniform(0.95, 1.05)
            
            # Distribución por estrato (realista para Colombia)
            total_residential = int(subscribers * 0.85)  # 85% residencial
            stratum_1 = int(total_residential * 0.25)  # 25%
            stratum_2 = int(total_residential * 0.30)  # 30%
            stratum_3 = int(total_residential * 0.25)  # 25%
            stratum_4 = int(total_residential * 0.10)  # 10%
            stratum_5 = int(total_residential * 0.07)  # 7%
            stratum_6 = int(total_residential * 0.03)  # 3%
            commercial = subscribers - total_residential  # 15% comercial
            
            vacant = int(subscribers * 0.05)  # 5% desocupados
            
            # Toneladas por tipo
            tons_sweeping = tons_non_recyclable * 0.08  # 8% barrido
            tons_urban_cleaning = tons_non_recyclable * 0.05  # 5% limpieza urbana
            tons_recyclable = tons_non_recyclable * 0.12  # 12% reciclable
            tons_rejection = tons_recyclable * 0.15  # 15% rechazo
            
            # Actividades de limpieza urbana (realistas)
            trees_pruned = random.randint(30, 80)
            cost_tree_pruning = trees_pruned * random.uniform(15000, 25000)
            grass_area = random.uniform(2000, 5000)
            public_areas_washed = random.uniform(1000, 3000)
            baskets_maintained = random.randint(50, 200)
            
            # Barrido
            sweeping_km = random.uniform(150, 400) if aps.segment == 1 else random.uniform(50, 150)
            
            # Disposición final y lixiviados
            tons_landfill = tons_non_recyclable * 1.08  # Incluye rechazos
            leachate_volume = tons_landfill * random.uniform(0.15, 0.25)  # ~20% en m³
            
            monthly_data = APSMonthlyData(
                aps_id=aps.id,
                period=period,
                year=year,
                month=month,
                
                # Suscriptores
                num_subscribers_total=subscribers,
                num_subscribers_occupied=subscribers - vacant,
                num_subscribers_vacant=vacant,
                num_subscribers_large_producers=int(commercial * 0.1),  # 10% grandes productores
                
                subscribers_stratum_1=stratum_1,
                subscribers_stratum_2=stratum_2,
                subscribers_stratum_3=stratum_3,
                subscribers_stratum_4=stratum_4,
                subscribers_stratum_5=stratum_5,
                subscribers_stratum_6=stratum_6,
                subscribers_commercial=commercial,
                
                # Toneladas
                tons_collected_non_recyclable=tons_non_recyclable,
                tons_collected_sweeping=tons_sweeping,
                tons_collected_urban_cleaning=tons_urban_cleaning,
                tons_collected_recyclable=tons_recyclable,
                tons_rejection_recycling=tons_rejection,
                
                # Limpieza urbana
                trees_pruned=trees_pruned,
                cost_tree_pruning=cost_tree_pruning,
                grass_area_cut_m2=grass_area,
                public_areas_washed_m2=public_areas_washed,
                beach_cleaning_m2=random.uniform(5000, 15000) if aps.is_coastal_municipality else 0,
                baskets_installed=random.randint(5, 15),
                baskets_maintained=baskets_maintained,
                
                # Barrido
                sweeping_length_km=sweeping_km,
                
                # Disposición final
                tons_received_landfill=tons_landfill,
                
                # Lixiviados
                leachate_volume_m3=leachate_volume,
                leachate_treatment_scenario=random.choice([2, 3, 4]),  # Escenarios comunes
                environmental_tax_rate=random.uniform(500, 1500),  # $/m³
                
                # Flota
                fleet_average_age_years=random.uniform(3, 8),
                fleet_daily_shifts=random.choice([1, 2]),
                
                verified=random.choice([True, False]),
                notes=f"Datos generados automáticamente para pruebas - {period}"
            )
            
            session.add(monthly_data)
            print(f"    ✅ {period}: {subscribers:,} suscriptores, {tons_non_recyclable:,.1f} ton")
    
    session.commit()
    
    # ========================================
    # RESUMEN FINAL
    # ========================================
    print("\n" + "="*60)
    print("✅ DATOS DE PRUEBA GENERADOS EXITOSAMENTE")
    print("="*60)
    print(f"\n📊 Resumen:")
    print(f"  • Empresas creadas: {len(companies)}")
    print(f"  • Usuarios creados: {len(users) + 1} (incluye SYSTEM)")
    print(f"  • APS creados: {len(aps_list)}")
    print(f"  • Meses de datos: 6 por cada APS")
    print(f"  • Total registros mensuales: {len(aps_list) * 6}")
    
    print(f"\n🔑 Credenciales de acceso:")
    print(f"  • SYSTEM: admin@system.com / admin123")
    for i, company in enumerate(companies):
        print(f"  • ADMIN {company.name}: admin@{company.name.lower().replace(' ', '').replace('.', '')[:20]}.com / admin123")
        print(f"  • USER {company.name}: operador@{company.name.lower().replace(' ', '').replace('.', '')[:20]}.com / user123")
    
    print(f"\n📍 APS disponibles para cálculos:")
    for aps in aps_list:
        print(f"  • ID {aps.id}: {aps.name} ({aps.code})")
        print(f"    Empresa: {aps.company_id}")
        print(f"    Segmento: {aps.segment}")
        print(f"    Datos mensuales: 2025-09 a 2026-02")
    
    print(f"\n🚀 Próximo paso:")
    print(f"  Puedes calcular tarifas usando:")
    print(f"  POST /api/tariff/calculate")
    print(f'  {{"aps_id": 1, "period": "2026-02", "calculation_type": "official"}}')
    
    print("\n" + "="*60)


if __name__ == "__main__":
    # Crear engine
    engine = create_engine(str(settings.DATABASE_URL))
    
    # Crear sesión
    with Session(engine) as session:
        try:
            generate_test_data(session)
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
