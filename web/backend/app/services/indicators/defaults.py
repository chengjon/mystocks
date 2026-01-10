"""
Indicator Defaults Loader
=========================

Migrates metadata from Legacy Registry to V2 Registry on startup.
"""
from typing import Dict, Any
from app.services.indicator_registry import IndicatorRegistry as LegacyRegistry
from app.services.indicators.indicator_registry import get_indicator_registry
from app.services.indicators.indicator_metadata import (
    IndicatorMetadata, IndicatorParameter, IndicatorOutput, 
    IndicatorCategory, PanelType, ParameterType, ParameterConstraint
)
from app.services.indicators.talib_adapter import register_all_talib_indicators
import logging

logger = logging.getLogger(__name__)

def load_default_indicators():
    """Load all default indicators into the V2 registry"""
    logger.info("Loading default indicators...")
    
    # 1. Register Adapters (Factories)
    register_all_talib_indicators()
    
    # 2. Migrate Metadata (Legacy -> V2)
    # Legacy registry initializes its data on __init__
    legacy = LegacyRegistry()
    v2_registry = get_indicator_registry()
    
    count = 0
    for abbr, data in legacy.get_all_indicators().items():
        try:
            # Map Category
            # Legacy stores it as Enum or String, handle both
            cat_raw = data.get("category", "trend")
            if hasattr(cat_raw, "value"):
                cat_raw = cat_raw.value
            
            # Simple mapping based on string value
            cat_map = {
                "trend": IndicatorCategory.TREND,
                "momentum": IndicatorCategory.MOMENTUM,
                "volatility": IndicatorCategory.VOLATILITY,
                "volume": IndicatorCategory.VOLUME,
                "candlestick": IndicatorCategory.CANDLESTICK
            }
            category = cat_map.get(str(cat_raw).lower(), IndicatorCategory.CUSTOM)

            # Map Panel
            panel_raw = data.get("panel_type", "overlay")
            if hasattr(panel_raw, "value"):
                panel_raw = panel_raw.value
            
            panel = PanelType.OVERLAY
            if str(panel_raw).lower() == "oscillator":
                panel = PanelType.OSCILLATOR
            
            # Map Parameters
            params = []
            for p in data.get("parameters", []):
                p_type = ParameterType.STRING
                legacy_type = p.get("type", "string")
                
                if legacy_type == "int": p_type = ParameterType.INT
                elif legacy_type == "float": p_type = ParameterType.FLOAT
                elif legacy_type == "bool": p_type = ParameterType.BOOL
                
                constraint = ParameterConstraint(
                    min_value=p.get("min"),
                    max_value=p.get("max")
                )
                
                params.append(IndicatorParameter(
                    name=p["name"],
                    type=p_type,
                    default=p["default"],
                    constraints=constraint,
                    description=p.get("description", "")
                ))
                
            # Map Outputs
            outputs = []
            for o in data.get("outputs", []):
                outputs.append(IndicatorOutput(
                    name=o["name"],
                    display_name=o.get("description", o["name"]), 
                    description=o.get("description", "")
                ))
            
            meta = IndicatorMetadata(
                abbreviation=abbr,
                full_name=data.get("full_name", abbr),
                chinese_name=data.get("chinese_name", abbr),
                category=category,
                description=data.get("description", ""),
                parameters=params,
                outputs=outputs,
                panel_type=panel,
                version="1.0.0"
            )
            
            v2_registry.register(meta)
            count += 1
            
        except Exception as e:
            logger.error(f"Failed to migrate {abbr}: {e}")
            
    logger.info(f"Successfully loaded {count} default indicators")
