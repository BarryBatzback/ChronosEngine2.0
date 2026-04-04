# test_visual.py
import asyncio
from services.blender_service import BlenderService

async def test_visual():
    blender = BlenderService({})
    
    if await blender.connect():
        print("✅ Connected to Blender")
        
        # Создаем визуально заметный объект
        test_code = """
import bpy

# Очищаем сцену
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Создаем большой красный куб
bpy.ops.mesh.primitive_cube_add(size=3, location=(0, 0, 1.5))

# Делаем его красным
mat = bpy.data.materials.new(name="RedMaterial")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1, 0, 0, 1)
bpy.context.active_object.data.materials.append(mat)

print("✅ Created big red cube - should be visible!")
"""
        
        print("🧪 Creating visible test object...")
        result = await blender.run_python(test_code)
        print("Creation result:", result)
        
        # Проверяем что объект создался
        check_code = """
import bpy
print(f"Objects in scene: {len(bpy.data.objects)}")
for obj in bpy.data.objects:
    print(f"  - {obj.name} at {obj.location}")
"""
        check_result = await blender.run_python(check_code)
        print("Scene check:", check_result)
        
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(test_visual())
