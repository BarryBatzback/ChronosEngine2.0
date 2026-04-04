# test_debug_import.py
import asyncio
from services.blender_service import BlenderService

async def test_debug_import():
    blender = BlenderService({})
    
    if await blender.connect():
        print("✅ Connected to Blender")
        
        # Простой тест одного ассета
        test_code = """
import bpy
import os

# Очищаем сцену
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Тестируем только blade
blade_path = 'assets/blades/basic_blade.blend'
print(f"Testing: {blade_path}")
print(f"Exists: {os.path.exists(blade_path)}")

# Пробуем импортировать
try:
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.append(
        filepath=blade_path,
        directory='assets/blades/',
        filename='*'
    )
    print(f"Imported: {len(bpy.context.selected_objects)} objects")
    
    # Логируем все объекты в сцене
    print("Scene objects:")
    for obj in bpy.data.objects:
        print(f"  - {obj.name} ({obj.type})")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
"""

        print("🧪 Running debug test...")
        result = await blender.run_python(test_code)
        print("Debug result:", result)
        
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(test_debug_import())
