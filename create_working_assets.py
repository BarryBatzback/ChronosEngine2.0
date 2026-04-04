# create_working_assets.py
"""
Скрипт для создания работающих ассетов - запускать в Blender!
"""

import bpy
from pathlib import Path

def create_working_assets():
    """Создает простые но работающие ассеты"""
    # Определяем путь к assets относительно скрипта Blender
    script_path = bpy.context.space_data.text.filepath
    assets_dir = Path(script_path).parent.parent / "assets"
    
    print(f"📁 Assets directory: {assets_dir}")
    
    # Создаем папки
    for category in ["blades", "handles", "guards"]:
        (assets_dir / category).mkdir(parents=True, exist_ok=True)
    
    # 1. Простое лезвие (обязательно в edit mode для экструзии)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)
    
    bpy.ops.mesh.primitive_plane_add(size=1.0, enter_editmode=True)
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, 0.5)})
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.resize(value=(0.1, 0.02, 1.0))
    bpy.ops.object.mode_set(mode='OBJECT')
    
    blade = bpy.context.active_object
    blade.name = "BladeMesh"  # Важно: понятное имя!
    
    blade_path = assets_dir / "blades" / "working_blade.blend"
    bpy.data.libraries.write(str(blade_path), {blade}, fake_user=True)
    print(f"✅ Created: {blade_path}")
    
    # 2. Простая рукоять
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.5, depth=1.0)
    handle = bpy.context.active_object
    handle.name = "HandleMesh"
    handle.scale = (0.04, 0.04, 0.3)
    bpy.ops.object.transform_apply(scale=True)
    
    handle_path = assets_dir / "handles" / "working_handle.blend"
    bpy.data.libraries.write(str(handle_path), {handle}, fake_user=True)
    print(f"✅ Created: {handle_path}")
    
    print("🎉 Working assets created!")
    print("💡 Restart Blender to use new assets")

# Запуск в Blender
if __name__ == "__main__":
    create_working_assets()
