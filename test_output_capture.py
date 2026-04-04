# test_output_capture.py
import asyncio
from services.blender_service import BlenderService

async def test_output_capture():
    blender = BlenderService({})
    
    if await blender.connect():
        print("✅ Connected to Blender")
        
        # Тест с выводом
        test_code = """
print("🔍 Testing output capture")
print("This should appear in response")
import bpy
print(f"Objects in scene: {len(bpy.data.objects)}")
for obj in bpy.data.objects:
    print(f"  - {obj.name}")
"""
        
        print("🧪 Testing output capture...")
        result = await blender.run_python(test_code)
        
        print("Full response:", result)
        
        if 'output' in result and result['output']:
            print("📝 Output from Blender:")
            print(result['output'])
        else:
            print("❌ No output captured")
            
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(test_output_capture())
