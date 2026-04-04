# test_fixed_server.py
import asyncio
from services.blender_service import BlenderService

async def test_fixed_server():
    blender = BlenderService({})
    
    if await blender.connect():
        print("✅ Connected to Blender")
        
        # Тест с выводом
        test_code = """
print("🔍 Testing fixed server output")
print("This should appear in response!")
import bpy
print(f"Objects in scene: {len(bpy.data.objects)}")
for obj in bpy.data.objects:
    print(f"  - {obj.name}")
"""
        
        print("🧪 Testing fixed server...")
        result = await blender.run_python(test_code)
        
        print("Full response:", result)
        
        if result.get('output'):
            print("🎉 OUTPUT CAPTURED!")
            print("Output content:", result['output'])
        else:
            print("❌ Still no output")
            
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(test_fixed_server())
