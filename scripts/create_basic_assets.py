# scripts/create_basic_assets.py
import bpy
from pathlib import Path


def create_basic_assets():
    """Создает базовые ассеты для тестирования"""
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)

    # Создаем папки компонентов
    (assets_dir / "blades").mkdir(exist_ok=True)
    (assets_dir / "handles").mkdir(exist_ok=True)
    (assets_dir / "guards").mkdir(exist_ok=True)

    print("🛠️ Creating basic assets...")

    # Простое лезвие
    bpy.ops.mesh.primitive_plane_add()
    blade = bpy.context.active_object
    blade.name = "BasicBlade"
    blade.scale = (0.1, 0.02, 1.0)
    bpy.ops.object.transform_apply(scale=True)

    # Сохраняем как ассет
    blade_path = assets_dir / "blades" / "basic_blade.blend"
    bpy.data.libraries.write(str(blade_path), {blade}, fake_user=True)

    # Простая рукоять
    bpy.ops.mesh.primitive_cylinder_add()
    handle = bpy.context.active_object
    handle.name = "BasicHandle"
    handle.scale = (0.03, 0.03, 0.3)
    bpy.ops.object.transform_apply(scale=True)

    handle_path = assets_dir / "handles" / "basic_handle.blend"
    bpy.data.libraries.write(str(handle_path), {handle}, fake_user=True)

    print("✅ Basic assets created!")


if __name__ == "__main__":
    create_basic_assets()
