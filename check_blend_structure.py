# check_blend_structure.py
import bpy
from pathlib import Path


def check_blend_structure():
    """Проверяет структуру .blend файлов"""
    assets_dir = Path("assets")

    print("🔍 Checking .blend file structure...")

    for blend_file in assets_dir.rglob("*.blend"):
        print(f"\n📁 File: {blend_file}")

        try:
            # Пробуем открыть файл
            with bpy.data.libraries.load(str(blend_file)) as (data_from, data_to):
                print(f"   Objects in file: {data_from.objects}")
                print(f"   Meshes in file: {data_from.meshes}")
                print(f"   Materials in file: {data_from.materials}")

        except Exception as e:
            print(f"   ❌ Error reading: {e}")


if __name__ == "__main__":
    check_blend_structure()
