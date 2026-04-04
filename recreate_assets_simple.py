# recreate_assets_simple.py
import bpy
from pathlib import Path

def create_simple_assets():
    """Создает простые ассеты с правильной структурой"""
    assets_dir = Path("assets")
    
    # Очищаем сцену
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)
    
    # 1. Простое лезвие
    bpy.ops.mesh.primitive_plane_add(size=1.0)
    blade = bpy.context.active_object
    blade.name = "Blade"  # ← Важно: понятное имя!
    blade.scale = (0.1, 0.02, 1.0)
    
    # Сохраняем
    blade_path = assets_dir / "blades" / "simple_blade.blend"
    bpy.data.libraries.write(str(blade_path), {blade}, fake_user=True)
    print(f"✅ Created: {blade_path}")
    
    # 2. Простая рукоять
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=1.0)
    handle = bpy.context.active_object
    handle.name = "Handle"  # ← Важно: понятное имя!
    handle.scale = (0.04, 0.04, 0.3)
    
    handle_path = assets_dir / "handles" / "simple_handle.blend"
    bpy.data.libraries.write(str(handle_path), {handle}, fake_user=True)
    print(f"✅ Created: {handle_path}")
    
    print("🎉 New assets created with proper structure!")

if __name__ == "__main__":
    create_simple_assets()
