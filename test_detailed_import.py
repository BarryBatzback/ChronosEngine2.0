# test_detailed_import.py
import asyncio
from services.blender_service import BlenderService

async def test_detailed_import():
    blender = BlenderService({})
    
    if await blender.connect():
        print("✅ Connected to Blender")
        
        # Детальный тест с полным выводом
        test_code = """
import bpy
import os

print("=" * 50)
print("🔍 DETAILED ASSET IMPORT TEST")
print("=" * 50)

# Очищаем сцену
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)
print("🧹 Scene cleared")

# Проверяем существование файла
blade_path = 'assets/blades/basic_blade.blend'
print(f"📁 Blade path exists: {os.path.exists(blade_path)}")

# Пробуем импортировать ВСЕ объекты
try:
    bpy.ops.object.select_all(action='DESELECT')
    print("🔄 Attempting to import ALL objects from blend file...")
    
    # Импортируем все объекты
    bpy.ops.wm.append(
        filepath=blade_path,
        directory='assets/blades/',
        filename='*'  # Все объекты
    )
    
    # Смотрим что импортировалось
    imported_objects = bpy.context.selected_objects
    print(f"📦 Imported {len(imported_objects)} objects")
    
    for obj in imported_objects:
        print(f"   • {obj.name} ({obj.type})")
        
    if imported_objects:
        # Настраиваем первый объект
        main_obj = imported_objects[0]
        main_obj.location = (0, 0, 1)
        main_obj.name = "TestBlade"
        print(f"✅ Setup complete: {main_obj.name}")
    else:
        print("❌ No objects were imported!")
        
except Exception as e:
    print(f"💥 Import error: {str(e)}")
    import traceback
    traceback.print_exc()

# Финальная проверка сцены
print("=" * 30)
print("🎯 FINAL SCENE STATE:")
print("=" * 30)
for obj in bpy.data.objects:
    print(f"   • {obj.name} ({obj.type}) at {obj.location}")

print("=" * 50)
print("Test completed!")
"""

        print("🧪 Running detailed test...")
        result = await blender.run_python(test_code)
        print("Test result:", result)
        
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(test_detailed_import())
