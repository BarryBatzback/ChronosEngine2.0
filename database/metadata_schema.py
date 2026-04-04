from pydantic import BaseModel
from typing import Dict, Optional

class AssetMetadata(BaseModel):
    asset_id: str
    source_type: str  # "hunyuan3d", "procedural", "scanned"
    category: str     # "blade", "handle", "guard"
    
    # Геометрические параметры (из референса)
    geometry_data: Dict[str, float] = {
        "length": 0.0,
        "width": 0.0,
        "curvature": 0.0
    }
    
    # Свойства материала (вариант 3)
    material_settings: Dict[str, any] = {
        "name": "historical_steel",
        "roughness": 0.4,
        "metalness": 1.0,
        "base_color_hex": "#7A7A7A"
    }