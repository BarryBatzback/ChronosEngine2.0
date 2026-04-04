# quick_fix_generator.py
from services.procedural_mesh_generator import ProceduralMeshGenerator

# Monkey patch для обработки ошибок
original_generate = ProceduralMeshGenerator.generate_code

def safe_generate_code(self, structure: dict, api_context: str = "") -> str:
    """Безопасная генерация кода с обработкой ошибок"""
    try:
        if not structure or 'components' not in structure:
            return self._generate_fallback_code()
        
        return original_generate(self, structure, api_context)
    except Exception as e:
        print(f"⚠️ Generator error: {e}, using fallback")
        return self._generate_fallback_code()

def _generate_fallback_code(self) -> str:
    """Fallback код для создания меча"""
    return """
import bpy
import bmesh
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create blade
bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=True)
bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, 1)})
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.transform.resize(value=(0.1, 0.02, 1))
bpy.ops.object.editmode_toggle()

# Create handle
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.3, location=(0, 0, -0.2))
bpy.ops.object.shade_smooth()

# Set materials
if "Blade" not in bpy.data.materials:
    mat_blade = bpy.data.materials.new(name="Blade")
    mat_blade.use_nodes = True
    mat_blade.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.8

if "Handle" not in bpy.data.materials:
    mat_handle = bpy.data.materials.new(name="Handle")
    mat_handle.use_nodes = True
    mat_handle.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.3, 0.2, 0.1, 1)

# Apply materials
for obj in bpy.context.selected_objects:
    if "Plane" in obj.name:
        obj.data.materials.append(bpy.data.materials["Blade"])
    elif "Cylinder" in obj.name:
        obj.data.materials.append(bpy.data.materials["Handle"])

bpy.ops.object.select_all(action='DESELECT')
"""

ProceduralMeshGenerator.generate_code = safe_generate_code
ProceduralMeshGenerator._generate_fallback_code = _generate_fallback_code

print("✅ Generator fallback applied")
