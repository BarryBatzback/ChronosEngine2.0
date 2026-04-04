# test_assets_manually.py
import asyncio
from services.blender_service import BlenderService

async def test_assets_manually():
    blender = BlenderService({})
    
    if await blender.connect():
        print("✅ Connected to Blender")
        
        # Тестируем каждый ассет отдельно
        tests = [
            {
                'name': 'Blade',
                'code': """
try:
    bpy.ops.wm.append(
        filepath='assets/blades/basic_blade.blend',
        directory='assets/blades/',
        filename='Object'
    )
    print("✅ Blade imported")
    print("Objects:", [obj.name for obj in bpy.data.objects])
except Exception as e:
    print("❌ Blade failed:", e)
"""
            },
            {
                'name': 'Handle', 
                'code': """
try:
    bpy.ops.wm.append(
        filepath='assets/handles/basic_handle.blend',
        directory='assets/handles/', 
        filename='Object'
    )
    print("✅ Handle imported")
    print("Objects:", [obj.name for obj in bpy.data.objects])
except Exception as e:
    print("❌ Handle failed:", e)
"""
            },
            {
                'name': 'Guard',
                'code': """
try:
    bpy.ops.wm.append(
        filepath='assets/guards/basic_guard.blend',
        directory='assets/guards/',
        filename='Object'
    )
    print("✅ Guard imported")
    print("Objects:", [obj.name for obj in bpy.data.objects])
except Exception as e:
    print("❌ Guard failed:", e)
"""
            }
        ]
        
        for test in tests:
            print(f"\n🧪 Testing {test['name']}...")
            result = await blender.run_python(test['code'])
            print(f"{test['name']} result:", result)
            
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(test_assets_manually())
