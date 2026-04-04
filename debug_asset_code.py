import bpy
from pathlib import Path

# Очистка сцены
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)


# Importing basic blade
try:
    bpy.ops.wm.append(
        filepath='assets\blades\basic_blade.blend',
        directory='assets\blades/',
        filename='Object'
    )
    imported_obj = bpy.context.selected_objects[0]
    imported_obj.location = [0, 0, 0.6]
    imported_obj.scale = (1.0, 1.0, 1.0)
    imported_obj.name = "basic_blade"
    print("✅ Asset imported successfully")
except Exception as e:
    print("❌ Asset import failed:", str(e))
    bpy.ops.mesh.primitive_plane_add(size=1, location=[0, 0, 0.6])


# Importing basic guard
try:
    bpy.ops.wm.append(
        filepath='assets\guards\basic_guard.blend',
        directory='assets\guards/',
        filename='Object'
    )
    imported_obj = bpy.context.selected_objects[0]
    imported_obj.location = [0, 0, 0.1]
    imported_obj.scale = (1.0, 1.0, 1.0)
    imported_obj.name = "basic_guard"
    print("✅ Asset imported successfully")
except Exception as e:
    print("❌ Asset import failed:", str(e))
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=[0, 0, 0.1])


# Importing basic handle
try:
    bpy.ops.wm.append(
        filepath='assets\handles\basic_handle.blend',
        directory='assets\handles/',
        filename='Object'
    )
    imported_obj = bpy.context.selected_objects[0]
    imported_obj.location = [0, 0, -0.3]
    imported_obj.scale = (1.0, 1.0, 1.0)
    imported_obj.name = "basic_handle"
    print("✅ Asset imported successfully")
except Exception as e:
    print("❌ Asset import failed:", str(e))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.3, location=[0, 0, -0.3])


# Финализация
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
bpy.ops.object.select_all(action='DESELECT')

print('Me4 sozdan iz assetov!')