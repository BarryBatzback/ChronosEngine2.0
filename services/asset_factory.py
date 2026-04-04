import json
import uuid
from pathlib import Path

class AssetFactory:
    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.registry_path = root_dir / "database" / "registry.json"
        self.load_registry()

    def load_registry(self):
        if self.registry_path.exists():
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                self.registry = json.load(f)
        else:
            self.registry = {"materials": {}, "meshes": {}}

    def generate_uid(self, prefix: str) -> str:
        """Генерирует уникальный ID: MAT_... или MSH_..."""
        return f"{prefix}_{uuid.uuid4().hex[:8].upper()}"

    def register_mesh(self, category: str, tags: list):
        """Регистрирует новый меш (например, из Hunyuan3D)"""
        uid = self.generate_uid("MSH")
        rel_path = f"assets/{category}/{uid}.blend"
        
        self.registry["meshes"][uid] = {
            "category": category,
            "rel_path": rel_path,
            "tags": tags,
            "status": "pending_refinement"
        }
        self.save_registry()
        return uid, rel_path

    def save_registry(self):
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2)