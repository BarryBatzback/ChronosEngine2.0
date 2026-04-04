# check_blend_structure_in_blender.py
"""
Скрипт для проверки структуры .blend файлов - запускать внутри Blender!
"""

import bpy
from pathlib import Path

def check_blend_structure():
    """Проверяет структуру .blend файлов"""
    assets_dir = Path(bpy.path.abspath("//../assets"))  # Папка assets рядом с проектом
    
    print("=" * 60)
    print("🔍 CHECKING .BLEND FILE STRUCTURE")
    print("=" * 60)
    
    for category in ["blades", "handles", "guards"]:
        category_dir = assets_dir / category
        if category_dir.exists():
            print(f"\n📁 Category: {category}")
            for blend_file in category_dir.glob("*.blend"):
                print(f"  📄 File: {blend_file.name}")
                
                try:
                    # Проверяем что есть в файле
                    with bpy.data.libraries.load(str(blend_file)) as (data_from, data_to):
                        if data_from.objects:
                            print(f"     Objects: {data_from.objects}")
                        else:
                            print(f"     ❌ NO OBJECTS FOUND!")
                            
                        if data_from.meshes:
                            print(f"     Meshes: {data_from.meshes}")
                            
                except Exception as e:
                    print(f"     ❌ Error: {e}")

if __name__ == "__main__":
    check_blend_structure()
