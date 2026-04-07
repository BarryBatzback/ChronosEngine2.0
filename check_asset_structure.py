# check_asset_structure.py
"""
Скрипт для проверки структуры ассетов - запускать в Blender!
"""

import bpy
from pathlib import Path


def check_asset_structure():
    """Проверяет что внутри .blend файлов"""
    assets_dir = Path("D:/ChronosEngine2.0/assets")  # ← АБСОЛЮТНЫЙ путь

    print("=" * 60)
    print("🔍 INSPECTING ASSET STRUCTURE")
    print("=" * 60)

    for category in ["blades", "handles", "guards"]:
        category_dir = assets_dir / category
        print(f"\n📁 {category.upper()}:")

        for blend_file in category_dir.glob("*.blend"):
            print(f"  📄 {blend_file.name}:")

            try:
                # Загружаем библиотеку
                with bpy.data.libraries.load(str(blend_file)) as (data_from, data_to):
                    print(f"    Objects: {data_from.objects}")
                    print(f"    Meshes: {data_from.meshes}")
                    print(f"    Materials: {data_from.materials}")

                    if data_from.objects:
                        # Пробуем импортировать
                        data_to.objects = data_from.objects
                        print(f"    ✅ Can load objects: {len(data_to.objects)}")
                    else:
                        print("    ❌ NO OBJECTS IN FILE!")

            except Exception as e:
                print(f"    💥 Error: {e}")


if __name__ == "__main__":
    check_asset_structure()
