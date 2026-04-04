# test_direct_execution.py
import asyncio
from services.blender_service import BlenderService

async def test_direct():
    blender = BlenderService({})
    
    if await blender.connect():
        print("✅ Connected to Blender")
        
        # Простой тест
        result = await blender.run_python("print('🚀 Direct test successful!')")
        print("Blender result:", result)
        
        # Тест с созданием куба
        cube_code = """
import bpy
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
print('✅ Cube created successfully!')
"""
        result = await blender.run_python(cube_code)
        print("Cube result:", result)
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(test_direct())

