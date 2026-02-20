"""Add APS and tariff calculation models

Revision ID: 001
Revises: 
Create Date: 2026-02-17 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create APS table
    op.create_table(
        'aps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('code', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('municipality', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('department', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('centroid_lat', sa.Float(), nullable=True),
        sa.Column('centroid_lon', sa.Float(), nullable=True),
        sa.Column('centroid_calculation_method', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('distance_to_landfill_km', sa.Float(), nullable=False),
        sa.Column('unpaved_road_percentage', sa.Float(), nullable=False),
        sa.Column('landfill_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('landfill_location', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('uses_transfer_station', sa.Boolean(), nullable=False),
        sa.Column('transfer_station_distance_km', sa.Float(), nullable=True),
        sa.Column('segment', sa.Integer(), nullable=False),
        sa.Column('is_coastal_municipality', sa.Boolean(), nullable=False),
        sa.Column('billing_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('billing_frequency', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_aps_code'), 'aps', ['code'], unique=True)
    op.create_index(op.f('ix_aps_company_id'), 'aps', ['company_id'], unique=False)
    op.create_index(op.f('ix_aps_created_at'), 'aps', ['created_at'], unique=False)
    op.create_index(op.f('ix_aps_is_active'), 'aps', ['is_active'], unique=False)
    op.create_index(op.f('ix_aps_name'), 'aps', ['name'], unique=False)
    
    # Create APS Monthly Data table
    op.create_table(
        'aps_monthly_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('aps_id', sa.Integer(), nullable=False),
        sa.Column('period', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('num_subscribers_total', sa.Integer(), nullable=False),
        sa.Column('num_subscribers_occupied', sa.Integer(), nullable=False),
        sa.Column('num_subscribers_vacant', sa.Integer(), nullable=False),
        sa.Column('num_subscribers_large_producers', sa.Integer(), nullable=False),
        sa.Column('subscribers_stratum_1', sa.Integer(), nullable=False),
        sa.Column('subscribers_stratum_2', sa.Integer(), nullable=False),
        sa.Column('subscribers_stratum_3', sa.Integer(), nullable=False),
        sa.Column('subscribers_stratum_4', sa.Integer(), nullable=False),
        sa.Column('subscribers_stratum_5', sa.Integer(), nullable=False),
        sa.Column('subscribers_stratum_6', sa.Integer(), nullable=False),
        sa.Column('subscribers_commercial', sa.Integer(), nullable=False),
        sa.Column('tons_collected_non_recyclable', sa.Float(), nullable=False),
        sa.Column('tons_collected_sweeping', sa.Float(), nullable=False),
        sa.Column('tons_collected_urban_cleaning', sa.Float(), nullable=False),
        sa.Column('tons_collected_recyclable', sa.Float(), nullable=False),
        sa.Column('tons_rejection_recycling', sa.Float(), nullable=False),
        sa.Column('trees_pruned', sa.Integer(), nullable=False),
        sa.Column('cost_tree_pruning', sa.Float(), nullable=False),
        sa.Column('grass_area_cut_m2', sa.Float(), nullable=False),
        sa.Column('public_areas_washed_m2', sa.Float(), nullable=False),
        sa.Column('beach_cleaning_m2', sa.Float(), nullable=False),
        sa.Column('beach_cleaning_km', sa.Float(), nullable=False),
        sa.Column('baskets_installed', sa.Integer(), nullable=False),
        sa.Column('baskets_maintained', sa.Integer(), nullable=False),
        sa.Column('sweeping_length_km', sa.Float(), nullable=False),
        sa.Column('sweeping_area_m2', sa.Float(), nullable=False),
        sa.Column('tons_received_landfill', sa.Float(), nullable=False),
        sa.Column('leachate_volume_m3', sa.Float(), nullable=False),
        sa.Column('leachate_treatment_scenario', sa.Integer(), nullable=False),
        sa.Column('environmental_tax_rate', sa.Float(), nullable=False),
        sa.Column('operational_costs', sa.JSON(), nullable=True),
        sa.Column('fleet_average_age_years', sa.Float(), nullable=False),
        sa.Column('fleet_daily_shifts', sa.Integer(), nullable=False),
        sa.Column('data_source', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('verified', sa.Boolean(), nullable=False),
        sa.Column('verified_by', sa.Integer(), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['aps_id'], ['aps.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_aps_monthly_data_aps_id'), 'aps_monthly_data', ['aps_id'], unique=False)
    op.create_index(op.f('ix_aps_monthly_data_month'), 'aps_monthly_data', ['month'], unique=False)
    op.create_index(op.f('ix_aps_monthly_data_period'), 'aps_monthly_data', ['period'], unique=False)
    op.create_index(op.f('ix_aps_monthly_data_year'), 'aps_monthly_data', ['year'], unique=False)
    
    # Create Tariff Calculation table
    op.create_table(
        'tariff_calculation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('aps_id', sa.Integer(), nullable=False),
        sa.Column('calculation_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('period', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('calculated_by', sa.Integer(), nullable=False),
        sa.Column('calculation_date', sa.DateTime(), nullable=False),
        
        # Costs
        sa.Column('cft', sa.Float(), nullable=False),
        sa.Column('ccs', sa.Float(), nullable=False),
        sa.Column('clus', sa.Float(), nullable=False),
        sa.Column('cbls', sa.Float(), nullable=False),
        sa.Column('clus_breakdown', sa.JSON(), nullable=True),
        sa.Column('cvna', sa.Float(), nullable=False),
        sa.Column('crt', sa.Float(), nullable=False),
        sa.Column('cdf', sa.Float(), nullable=False),
        sa.Column('ctl', sa.Float(), nullable=False),
        
        # CRT details
        sa.Column('crt_function_used', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('crt_distance_km', sa.Float(), nullable=False),
        sa.Column('crt_avg_tons', sa.Float(), nullable=False),
        sa.Column('crt_tolls', sa.Float(), nullable=False),
        sa.Column('crt_coastal_adjustment', sa.Boolean(), nullable=False),
        sa.Column('crt_fleet_age_discount', sa.Float(), nullable=False),
        
        # CDF details
        sa.Column('cdf_vu', sa.Float(), nullable=False),
        sa.Column('cdf_pc', sa.Float(), nullable=False),
        sa.Column('cdf_avg_tons_landfill', sa.Float(), nullable=False),
        sa.Column('cdf_adjustment_small_landfill', sa.Float(), nullable=False),
        
        # CTL details
        sa.Column('ctl_scenario', sa.Integer(), nullable=False),
        sa.Column('ctl_volume_m3', sa.Float(), nullable=False),
        sa.Column('ctl_environmental_tax', sa.Float(), nullable=False),
        sa.Column('ctl_vu', sa.Float(), nullable=False),
        sa.Column('ctl_pc', sa.Float(), nullable=False),
        
        # VBA
        sa.Column('vba', sa.Float(), nullable=False),
        sa.Column('vba_incentive_discount', sa.Float(), nullable=False),
        
        # Tons per subscriber
        sa.Column('trbl', sa.Float(), nullable=False),
        sa.Column('trlu', sa.Float(), nullable=False),
        sa.Column('trra', sa.Float(), nullable=False),
        sa.Column('tra', sa.Float(), nullable=False),
        sa.Column('trna_stratum_1', sa.Float(), nullable=False),
        sa.Column('trna_stratum_2', sa.Float(), nullable=False),
        sa.Column('trna_stratum_3', sa.Float(), nullable=False),
        sa.Column('trna_stratum_4', sa.Float(), nullable=False),
        sa.Column('trna_stratum_5', sa.Float(), nullable=False),
        sa.Column('trna_stratum_6', sa.Float(), nullable=False),
        sa.Column('trna_commercial', sa.Float(), nullable=False),
        
        # Tariffs
        sa.Column('tariff_stratum_1_base', sa.Float(), nullable=False),
        sa.Column('tariff_stratum_2_base', sa.Float(), nullable=False),
        sa.Column('tariff_stratum_3_base', sa.Float(), nullable=False),
        sa.Column('tariff_stratum_4_base', sa.Float(), nullable=False),
        sa.Column('tariff_stratum_5_base', sa.Float(), nullable=False),
        sa.Column('tariff_stratum_6_base', sa.Float(), nullable=False),
        sa.Column('tariff_commercial_base', sa.Float(), nullable=False),
        sa.Column('tariff_stratum_1_final', sa.Float(), nullable=False),
        sa.Column('tariff_stratum_2_final', sa.Float(), nullable=False),
        sa.Column('tariff_stratum_3_final', sa.Float(), nullable=False),
        sa.Column('tariff_stratum_4_final', sa.Float(), nullable=False),
        sa.Column('tariff_stratum_5_final', sa.Float(), nullable=False),
        sa.Column('tariff_stratum_6_final', sa.Float(), nullable=False),
        sa.Column('tariff_commercial_final', sa.Float(), nullable=False),
        
        # Metadata
        sa.Column('subsidy_contribution_factors', sa.JSON(), nullable=True),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('formulas_used', sa.JSON(), nullable=True),
        sa.Column('regulatory_references', sa.JSON(), nullable=True),
        sa.Column('validations', sa.JSON(), nullable=True),
        sa.Column('is_simulation', sa.Boolean(), nullable=False),
        sa.Column('simulation_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('notes', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('comparison_with', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        
        sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
        sa.ForeignKeyConstraint(['aps_id'], ['aps.id'], ),
        sa.ForeignKeyConstraint(['calculated_by'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tariff_calculation_aps_id'), 'tariff_calculation', ['aps_id'], unique=False)
    op.create_index(op.f('ix_tariff_calculation_company_id'), 'tariff_calculation', ['company_id'], unique=False)
    op.create_index(op.f('ix_tariff_calculation_period'), 'tariff_calculation', ['period'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_tariff_calculation_period'), table_name='tariff_calculation')
    op.drop_index(op.f('ix_tariff_calculation_company_id'), table_name='tariff_calculation')
    op.drop_index(op.f('ix_tariff_calculation_aps_id'), table_name='tariff_calculation')
    op.drop_table('tariff_calculation')
    
    op.drop_index(op.f('ix_aps_monthly_data_year'), table_name='aps_monthly_data')
    op.drop_index(op.f('ix_aps_monthly_data_period'), table_name='aps_monthly_data')
    op.drop_index(op.f('ix_aps_monthly_data_month'), table_name='aps_monthly_data')
    op.drop_index(op.f('ix_aps_monthly_data_aps_id'), table_name='aps_monthly_data')
    op.drop_table('aps_monthly_data')
    
    op.drop_index(op.f('ix_aps_name'), table_name='aps')
    op.drop_index(op.f('ix_aps_is_active'), table_name='aps')
    op.drop_index(op.f('ix_aps_created_at'), table_name='aps')
    op.drop_index(op.f('ix_aps_company_id'), table_name='aps')
    op.drop_index(op.f('ix_aps_code'), table_name='aps')
    op.drop_table('aps')
