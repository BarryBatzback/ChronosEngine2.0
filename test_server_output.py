# test_server_output.py
import asyncio
from services.blender_service import BlenderService

async def test_server_output():
    blender = BlenderService({})
    
    if await blender.connect():
        print("✅ Connected to Blender")
        
        # Простой тест с выводом
        test_code = """
print("🔍 Testing server output capture")
print("This should appear in response")
import bpy
print(f"Objects in scene: {len(bpy.data.objects)}")
"""
        
        print("🧪 Testing output capture...")
        result = await blender.run_python(test_code)
        print("Full response:", result)
        
        if 'output' in result:
            print("📝 Output from Blender:")
            print(result['output'])
        else:
            print("❌ No output in response")
            
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(test_server_output())
