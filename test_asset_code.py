# test_asset_code.py
import asyncio
from services.blender_service import BlenderService

async def test_asset_code():
    blender = BlenderService({})
    
    if await blender.connect():
        print("✅ Connected to Blender")
        
        # Читаем сгенерированный код
        with open("debug_asset_code.py", "r", encoding="utf-8") as f:
            asset_code = f.read()
        
        print("📝 Testing asset code...")
        result = await blender.run_python(asset_code)
        print("Asset code result:", result)
        
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(test_asset_code())
