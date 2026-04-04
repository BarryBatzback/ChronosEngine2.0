# test_with_file_logging.py
import asyncio
from services.blender_service import BlenderService

async def test_with_logging():
    blender = BlenderService({})
    
    if await blender.connect():
        print("✅ Connected to Blender")
        
        # Тестовый код с выводом
        test_code = """
import bpy
import os

print("🔍 Testing asset import...")
print(f"Blade path: assets/blades/basic_blade.blend")
print(f"Exists: {os.path.exists('assets/blades/basic_blade.blend')}")

# Пробуем импортировать
try:
    bpy.ops.object.select_all(action='DESELECT')
    print("🔄 Attempting import...")
    
    bpy.ops.wm.append(
        filepath='assets/blades/basic_blade.blend',
        directory='assets/blades/',
        filename='*'
    )
    
    imported_count = len(bpy.context.selected_objects)
    print(f"📦 Imported {imported_count} objects")
    
    for obj in bpy.context.selected_objects:
        print(f"   • {obj.name}")
        
except Exception as e:
    print(f"💥 Error: {e}")
    import traceback
    traceback.print_exc()

print("✅ Test completed")
"""
        
        print("🧪 Running test with file logging...")
        result = await blender.run_python(test_code)
        print("Result status:", result['status'])
        
        # Читаем лог файл
        try:
            with open(r"D:\blender_debug.log", "r", encoding="utf-8") as f:
                log_content = f.read()
                print("📝 Blender log:")
                print(log_content[-1000:])  # Последние 1000 символов
        except FileNotFoundError:
            print("❌ Log file not found")
            
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(test_with_logging())
