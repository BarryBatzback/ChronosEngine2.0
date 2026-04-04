# test_fixed_import.py
import asyncio
from services.blender_service import BlenderService

async def test_fixed_import():
    blender = BlenderService({})
    
    if await blender.connect():
        print("✅ Connected to Blender")
        
        # Тест с правильным именем объекта
        test_code = """
import bpy
import os

# Очищаем сцену
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Импортируем с ПРАВИЛЬНЫМ именем
blade_path = 'assets/blades/basic_blade.blend'
print(f"Importing: {blade_path}")

try:
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.append(
        filepath=blade_path,
        directory='assets/blades/',
        filename='BasicSwordBlade'  # ← Правильное имя!
    )
    
    imported_count = len(bpy.context.selected_objects)
    print(f"✅ Imported {imported_count} objects")
    
    for obj in bpy.context.selected_objects:
        print(f"   • {obj.name}")
        obj.location = (0, 0, 1)  # Перемещаем для видимости
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Финальная проверка
print("Scene objects:")
for obj in bpy.data.objects:
    print(f"  - {obj.name} at {obj.location}")
"""

        print("🧪 Testing fixed import...")
        result = await blender.run_python(test_code)
        print("Test completed!")
        
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(test_fixed_import())
