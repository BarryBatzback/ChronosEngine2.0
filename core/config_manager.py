import os
from pathlib import Path

class ConfigManager:
    def __init__(self):
        # Динамическое определение корня проекта
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.ASSETS_DIR = self.BASE_DIR / "assets"
        self.DATABASE_DIR = self.BASE_DIR / "database"
        self.OUTPUT_DIR = self.BASE_DIR / "output"
        
        # Создаем структуру, если её нет
        for folder in [self.ASSETS_DIR, self.DATABASE_DIR, self.OUTPUT_DIR]:
            folder.mkdir(parents=True, exist_ok=True)
            
    def get_asset_path(self, category: str, filename: str) -> str:
        path = self.ASSETS_DIR / category / filename
        return str(path).replace("\\", "/") # Blender любит прямые слеши даже на Windows