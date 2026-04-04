# services/component_library.py (исправляем пути)
import sys
from pathlib import Path
import json
from pathlib import Path
from typing import Dict, Optional
from loguru import logger

class ComponentLibrary:
    def __init__(self, assets_path: str = "assets"):
        self.assets_path = Path(assets_path)
        self.components = self._initialize_component_library()
        logger.info(f"📦 ComponentLibrary initialized with assets from: {self.assets_path}")
        
    def _initialize_component_library(self) -> Dict:
        """Инициализирует библиотеку компонентов"""
        return {
            'sword': {
                'blade': {
                    'basic': {'file': 'blades/basic_blade.blend', 'scale': 1.0, 'material': 'metal'}
                },
                'handle': {
                    'basic': {'file': 'handles/basic_handle.blend', 'scale': 1.0, 'material': 'wood'}
                },
                'guard': {
                    'basic': {'file': 'guards/basic_guard.blend', 'scale': 1.0, 'material': 'metal'}
                }
            }
        }
    
    def get_component(self, category: str, component_type: str, style: str = 'basic') -> Optional[Dict]:
        """Возвращает информацию о компоненте"""
        try:
            comp = self.components[category][component_type][style].copy()
            comp['file'] = str(self.assets_path / comp['file'])
            return comp
        except KeyError:
            logger.warning(f"Component not found: {category}/{component_type}/{style}")
            return None

    # services/component_library.py (ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ)
    def import_component_code(self, category: str, component_type: str, style: str, position: list) -> str:
        comp = self.get_component(category, component_type, style)
        if not comp:
            return self._generate_primitive_fallback(component_type, position)
        
        filepath = comp['file'].replace('\\', '/')
        directory = str(Path(filepath).parent).replace('\\', '/')
        object_name = 'SwordBlade'
        
        # 🔥 УБИРАЕМ ВСЕ ОТСТУПЫ - каждая строка должна начинаться с начала
        return f"""import bpy
    import os

    print("=" * 40)
    print(f"🔧 IMPORTING {component_type.upper()}")
    print("=" * 40)

    print(f"Filepath: {filepath}")
    print(f"Object name: {object_name}")
    print(f"File exists: {{os.path.exists('{filepath}')}}")

    try:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.wm.append(
            filepath='{filepath}',
            directory='{directory}/',
            filename='{object_name}'
        )
        
        imported_objects = bpy.context.selected_objects
        print(f"📦 Imported {{len(imported_objects)}} objects")
        
        for obj in imported_objects:
            print(f"   • {{obj.name}} ({{obj.type}})")
        
        if imported_objects:
            imported_obj = imported_objects[0]
            imported_obj.location = {position}
            imported_obj.scale = ({comp['scale']}, {comp['scale']}, {comp['scale']})
            imported_obj.name = "{style}_{component_type}"
            print(f"✅ Success: {{imported_obj.name}}")
        else:
            print("❌ Import failed - no objects")
            {self._generate_primitive_fallback(component_type, position)}
            
    except Exception as e:
        print(f"💥 Import error: {{str(e)}}")
        import traceback
        traceback.print_exc()
        {self._generate_primitive_fallback(component_type, position)}

    print("=" * 40)
    """

    def _generate_primitive_fallback(self, component_type: str, position: list) -> str:
        """Генерация fallback кода"""
        if component_type == 'blade':
            return f"bpy.ops.mesh.primitive_plane_add(size=1, location={position})"
        elif component_type == 'handle':
            return f"bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.3, location={position})"
        elif component_type == 'guard':
            return f"bpy.ops.mesh.primitive_cube_add(size=0.2, location={position})"
        else:
            return f"bpy.ops.mesh.primitive_cube_add(size=1, location={position})"


    def has_assets(self) -> bool:
        """Проверяет наличие ассетов"""
        return (self.assets_path / "blades" / "basic_blade.blend").exists()
