# test_direct_creation.py
import asyncio
from services.blender_service import BlenderService

async def test_direct_creation():
    blender = BlenderService({})
    
    if await blender.connect():
        print("✅ Connected to Blender")
        
        # Тест прямого создания меша
        test_code = """
import bpy
import bmesh
from mathutils import Vector

# Очистка
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Создаем простой меш
bm = bmesh.new()
bm.verts.new(Vector((-0.5, -0.5, 0)))
bm.verts.new(Vector((0.5, -0.5, 0)))
bm.verts.new(Vector((0.5, 0.5, 0)))
bm.verts.new(Vector((-0.5, 0.5, 0)))
bm.verts.ensure_lookup_table()
bm.faces.new(bm.verts)
mesh = bpy.data.meshes.new('test_mesh')
bm.to_mesh(mesh)
bm.free()
obj = bpy.data.objects.new('test_object', mesh)
bpy.context.collection.objects.link(obj)

print("✅ Mesh created from scratch!")
print(f"Objects: {len(bpy.data.objects)}")
"""

        print("🧪 Testing direct mesh creation...")
        result = await blender.run_python(test_code)
        print("Result:", result)
        
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(test_direct_creation())
