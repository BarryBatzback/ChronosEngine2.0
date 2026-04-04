import json
from pathlib import Path

class ReferenceService:
    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.refs_path = root_dir / "docs" / "historical_references"
        self.refs_path.mkdir(exist_ok=True)

    def get_material_blueprint(self, material_name: str):
        """Возвращает настройки материала из базы (Вариант 3)"""
        # Здесь мы можем хранить пресеты: 'viking_iron', 'pattern_welded_steel'
        presets = {
            "viking_iron": {"roughness": 0.6, "metalness": 0.9, "color": [0.2, 0.2, 0.2, 1]},
            "damascus_steel": {"roughness": 0.3, "metalness": 1.0, "color": [0.4, 0.4, 0.4, 1]}
        }
        return presets.get(material_name, presets["viking_iron"])