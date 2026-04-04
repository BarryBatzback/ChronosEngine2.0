# test_file_output.py
import asyncio
from services.blender_service import BlenderService

async def test_file_output():
    blender = BlenderService({})
    
    if await blender.connect():
        print("✅ Connected to Blender")
        
        # Простой тест
        test_code = """
print("🔍 Testing file output")
print("This should be captured")
import bpy
print(f"Scene objects: {len(bpy.data.objects)}")
"""
        
        print("🧪 Testing file output capture...")
        result = await blender.run_python_with_output(test_code)
        print("Result with output:", result)
        
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(test_file_output())
