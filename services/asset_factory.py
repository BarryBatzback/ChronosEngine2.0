import json
import uuid
import logging
from pathlib import Path
from typing import Dict, Optional, Any

class AssetFactory:
    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.registry_path = self.root / "database" / "registry.json"
        self.assets_dir = self.root / "assets"
        
        # Гарантируем наличие базы
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.load_registry()

    def load_registry(self):
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    self.registry = json.load(f)
            except json.JSONDecodeError:
                logging.error("Registry file is corrupted. Resetting.")
                self.registry = {"materials": {}, "meshes": {}, "metadata": {"version": "2.0"}}
        else:
            self.registry = {"materials": {}, "meshes": {}, "metadata": {"version": "2.0"}}
            self.save_registry()

    def save_registry(self):
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=4, ensure_ascii=False)

    def get_asset_info(self, uid: str) -> Optional[Dict]:
        """Получить полные данные об ассете по его ID"""
        return self.registry["meshes"].get(uid) or self.registry["materials"].get(uid)

    def register_new_mesh(self, category: str, sub_type: str, metadata: Dict[str, Any]) -> str:
        """
        Регистрация нового меша в системе.
        Пример: category='weapons', sub_type='blades'
        """
        uid = f"MSH_{category.upper()[:3]}_{uuid.uuid4().hex[:6].upper()}"
        rel_path = f"assets/{category}/{sub_type}/{uid}.blend"
        
        # Создаем физическую папку
        (self.root / rel_path).parent.mkdir(parents=True, exist_ok=True)

        self.registry["meshes"][uid] = {
            "uid": uid,
            "path": rel_path,
            "category": category,
            "sub_type": sub_type,
            "metadata": metadata,
            "status": "raw"
        }
        self.save_registry()
        return uid

    def create_blender_import_script(self, uid: str) -> str:
        """Генерирует идеальный код импорта для Blender на основе UID"""
        asset = self.get_asset_info(uid)
        if not asset:
            return "# Error: Asset UID not found"

        abs_path = (self.root / asset['path']).as_posix()
        
        return f"""
import bpy
import os

def import_chronos_asset():
    path = "{abs_path}"
    if not os.path.exists(path):
        print(f"Error: File not found {{path}}")
        return

    # Импорт объекта по UID через библиотеку
    with bpy.data.libraries.load(path, link=False) as (data_from, data_to):
        data_to.objects = data_from.objects

    for obj in data_to.objects:
        if obj is not None:
            bpy.context.collection.objects.link(obj)
            obj["chronos_uid"] = "{uid}" # Метка для синхронизации
            print(f"Successfully imported: {{obj.name}} with UID {uid}")

import_chronos_asset()
"""