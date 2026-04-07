# check_blender_scene.py
import asyncio
from services.blender_service import BlenderService


async def check_scene():
    blender = BlenderService({})

    if await blender.connect():
        print("✅ Connected to Blender")

        # Получаем информацию о сцене
        scene_info = await blender.get_scene_info()
        print("📊 Scene info:", scene_info)

        # Считаем объекты
        count_code = """
import bpy
object_count = len(bpy.data.objects)
object_names = [obj.name for obj in bpy.data.objects]
print(f"Object count: {object_count}")
print(f"Object names: {object_names}")
"""
        result = await blender.run_python(count_code)
        print("Object count result:", result)

    else:
        print("❌ Failed to connect")


if __name__ == "__main__":
    asyncio.run(check_scene())
