"""SWMM Object Enum."""
from swmm.toolkit import shared_enum

subcatch_attribute = dict(
    rainfall=shared_enum.SubcatchAttribute.RAINFALL,
    snow_depth=shared_enum.SubcatchAttribute.SNOW_DEPTH,
    evap_loss=shared_enum.SubcatchAttribute.EVAP_LOSS,
    infil_loss=shared_enum.SubcatchAttribute.INFIL_LOSS,
    runoff_rate=shared_enum.SubcatchAttribute.RUNOFF_RATE,
    gw_outflow_rate=shared_enum.SubcatchAttribute.GW_OUTFLOW_RATE,
    gw_table_elev=shared_enum.SubcatchAttribute.GW_TABLE_ELEV,
    soil_moisture=shared_enum.SubcatchAttribute.SOIL_MOISTURE,
)

node_attribute = dict(
    invert_depth=shared_enum.NodeAttribute.INVERT_DEPTH,
    hydraulic_head=shared_enum.NodeAttribute.HYDRAULIC_HEAD,
    ponded_volume=shared_enum.NodeAttribute.PONDED_VOLUME,
    lateral_inflow=shared_enum.NodeAttribute.LATERAL_INFLOW,
    total_inflow=shared_enum.NodeAttribute.TOTAL_INFLOW,
    flooding_losses=shared_enum.NodeAttribute.FLOODING_LOSSES,
)

link_attribute = dict(
    flow_rate=shared_enum.LinkAttribute.FLOW_RATE,
    flow_depth=shared_enum.LinkAttribute.FLOW_DEPTH,
    flow_velocity=shared_enum.LinkAttribute.FLOW_VELOCITY,
    flow_volume=shared_enum.LinkAttribute.FLOW_VOLUME,
    capacity=shared_enum.LinkAttribute.CAPACITY,
)

system_attribute = dict(
    air_temp=shared_enum.SystemAttribute.AIR_TEMP,
    rainfall=shared_enum.SystemAttribute.RAINFALL,
    snow_depth=shared_enum.SystemAttribute.SNOW_DEPTH,
    evap_infil_loss=shared_enum.SystemAttribute.EVAP_INFIL_LOSS,
    runoff_flow=shared_enum.SystemAttribute.RUNOFF_FLOW,
    dry_weather_inflow=shared_enum.SystemAttribute.DRY_WEATHER_INFLOW,
    gw_inflow=shared_enum.SystemAttribute.GW_INFLOW,
    rdii_inflow=shared_enum.SystemAttribute.RDII_INFLOW,
    direct_inflow=shared_enum.SystemAttribute.DIRECT_INFLOW,
    total_lateral_inflow=shared_enum.SystemAttribute.TOTAL_LATERAL_INFLOW,
    flood_losses=shared_enum.SystemAttribute.FLOOD_LOSSES,
    outfall_flows=shared_enum.SystemAttribute.OUTFALL_FLOWS,
    volume_stored=shared_enum.SystemAttribute.VOLUME_STORED,
    evap_rate=shared_enum.SystemAttribute.EVAP_RATE,
    ptnl_evap_rate=shared_enum.SystemAttribute.PTNL_EVAP_RATE,
)
