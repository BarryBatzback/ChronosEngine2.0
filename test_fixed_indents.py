# test_fixed_indents.py
import asyncio
from services.blender_service import BlenderService

async def test_fixed_indents():
    blender = BlenderService({})
    
    if await blender.connect():
        print("✅ Connected to Blender")
        
        # Тест с исправленными отступами
        test_code = """import bpy
import os

print("🔍 Testing fixed indents")
print("This should work now!")
print(f"Objects in scene: {len(bpy.data.objects)}")
"""
        
        print("🧪 Testing fixed indents...")
        result = await blender.run_python(test_code)
        
        print("Full response:", result)
        
        if 'output' in result and result['output']:
            print("🎉 OUTPUT CAPTURED!")
            print("Output content:", repr(result['output']))
        else:
            print("❌ Still no output")
            
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(test_fixed_indents())
