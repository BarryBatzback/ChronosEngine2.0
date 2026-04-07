# scripts/create_basic_assets_blender.py
"""
Скрипт для создания базовых ассетов - запускать через:
D:\blender5.1\blender.exe --background --python scripts/create_basic_assets_blender.py
"""

import bpy
import os
from pathlib import Path


def setup_directories():
    """Настраивает директории для ассетов"""
    # Определяем путь к assets относительно скрипта
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = script_dir.parent / "assets"

    # Создаем папки компонентов
    blades_dir = assets_dir / "blades"
    handles_dir = assets_dir / "handles"
    guards_dir = assets_dir / "guards"
    materials_dir = assets_dir / "materials"

    for directory in [assets_dir, blades_dir, handles_dir, guards_dir, materials_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    return assets_dir


def create_basic_blade(assets_dir):
    """Создает базовое лезвие меча"""
    # Очищаем сцену
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False, confirm=False)

    # Создаем плоскость для лезвия
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, 0))
    blade = bpy.context.active_object
    blade.name = "BasicSwordBlade"

    # Переходим в edit mode для экструзии
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, 0.5)})
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.transform.resize(value=(0.08, 0.015, 1.0))
    bpy.ops.object.mode_set(mode="OBJECT")

    # Применяем трансформации
    bpy.ops.object.transform_apply(scale=True, location=True, rotation=True)

    # Сохраняем как ассет
    blade_path = assets_dir / "blades" / "basic_blade.blend"
    bpy.data.libraries.write(str(blade_path), {blade}, fake_user=True)

    print(f"✅ Created blade: {blade_path}")
    return blade_path


def create_basic_handle(assets_dir):
    """Создает базовую рукоять"""
    bpy.ops.object.select_all(action="DESELECT")

    # Создаем цилиндр для рукояти
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.5, depth=1.0, location=(0, 0, 0)
    )
    handle = bpy.context.active_object
    handle.name = "BasicSwordHandle"

    # Масштабируем
    handle.scale = (0.04, 0.04, 0.25)
    bpy.ops.object.transform_apply(scale=True)

    # Сглаживаем
    bpy.ops.object.shade_smooth()

    # Сохраняем
    handle_path = assets_dir / "handles" / "basic_handle.blend"
    bpy.data.libraries.write(str(handle_path), {handle}, fake_user=True)

    print(f"✅ Created handle: {handle_path}")
    return handle_path


def create_basic_guard(assets_dir):
    """Создает базовую гарду"""
    bpy.ops.object.select_all(action="DESELECT")

    # Создаем куб для гарды
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    guard = bpy.context.active_object
    guard.name = "BasicSwordGuard"

    # Масштабируем
    guard.scale = (0.2, 0.05, 0.03)
    bpy.ops.object.transform_apply(scale=True)

    # Сохраняем
    guard_path = assets_dir / "guards" / "basic_guard.blend"
    bpy.data.libraries.write(str(guard_path), {guard}, fake_user=True)

    print(f"✅ Created guard: {guard_path}")
    return guard_path


def create_basic_materials(assets_dir):
    """Создает базовые материалы"""
    materials_dir = assets_dir / "materials"

    # Металлический материал
    metal_mat = bpy.data.materials.new(name="MetalMaterial")
    metal_mat.use_nodes = True
    bsdf = metal_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Metallic"].default_value = 0.8
    bsdf.inputs["Roughness"].default_value = 0.3
    bsdf.inputs["Base Color"].default_value = (0.8, 0.8, 0.9, 1.0)

    # Деревянный материал
    wood_mat = bpy.data.materials.new(name="WoodMaterial")
    wood_mat.use_nodes = True
    bsdf = wood_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.7
    bsdf.inputs["Base Color"].default_value = (0.35, 0.25, 0.15, 1.0)

    # Сохраняем материалы
    materials_path = materials_dir / "basic_materials.blend"
    bpy.data.libraries.write(
        str(materials_path), set(bpy.data.materials), fake_user=True
    )

    print(f"✅ Created materials: {materials_path}")
    return materials_path


def main():
    """Основная функция создания ассетов"""
    print("=" * 60)
    print("🛠️  CREATING BASIC ASSETS FOR CHRONOS ENGINE")
    print("=" * 60)

    # Настраиваем директории
    assets_dir = setup_directories()
    print(f"📁 Assets directory: {assets_dir}")

    # Создаем компоненты
    blade_path = create_basic_blade(assets_dir)
    handle_path = create_basic_handle(assets_dir)
    guard_path = create_basic_guard(assets_dir)
    materials_path = create_basic_materials(assets_dir)

    # Очищаем сцену
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False, confirm=False)

    print("=" * 60)
    print("🎉 ASSETS CREATION COMPLETED!")
    print("📦 Created components:")
    print(f"   • Blade: {blade_path}")
    print(f"   • Handle: {handle_path}")
    print(f"   • Guard: {guard_path}")
    print(f"   • Materials: {materials_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
