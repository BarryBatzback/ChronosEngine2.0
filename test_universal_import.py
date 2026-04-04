# test_universal_import.py
import asyncio
from services.blender_service import BlenderService

async def test_universal_import():
    blender = BlenderService({})
    
    if await blender.connect():
        print("✅ Connected to Blender")
        
        # Тест универсального импорта
        test_code = """
import bpy

# Очищаем сцену
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Универсальный импорт лезвия
try:
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.append(
        filepath='assets/blades/basic_blade.blend',
        directory='assets/blades/',
        filename='*'  # Импортируем ВСЕ объекты
    )
    print("✅ Imported objects:", [obj.name for obj in bpy.context.selected_objects])
except Exception as e:
    print("❌ Import failed:", e)

# Проверяем что в сцене
print("Objects in scene:", [obj.name for obj in bpy.data.objects])
"""
        
        result = await blender.run_python(test_code)
        print("Universal import result:", result)
        
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(test_universal_import())
