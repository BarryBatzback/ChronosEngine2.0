# test_clean_code.py
import asyncio
from services.blender_service import BlenderService

async def test_clean_code():
    blender = BlenderService({})
    
    if await blender.connect():
        print("✅ Connected to Blender")
        
        # Простой чистый код без отступов
        test_code = "import bpy\nprint('✅ Clean code test')\nprint(f'Objects: {len(bpy.data.objects)}')"
        
        print("🧪 Testing clean code...")
        result = await blender.run_python(test_code)
        print("Clean code result:", result)
        
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(test_clean_code())
