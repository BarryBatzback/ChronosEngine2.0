"""
Процедурная генерация мешей на основе семантической структуры
Следует рекомендациям официальной документации Blender API
"""

from typing import Dict, List


# services/procedural_mesh_generator.py (ПЕРЕПИСЫВАЕМ)
class ProceduralMeshGenerator:
    def generate_code(self, structure: dict, context: str = None) -> str:
        code = [
            "import bpy",
            "import math",
            "",
            "def clean_scene():",
            "    # Переключаемся в объектный режим, если мы в Edit Mode",
            "    if bpy.context.view_layer.objects.active and bpy.context.view_layer.objects.active.mode != 'OBJECT':",
            "        bpy.ops.object.mode_set(mode='OBJECT')",
            "    # Удаляем всё",
            "    bpy.ops.object.select_all(action='SELECT')",
            "    bpy.ops.object.delete()",
            "",
            "clean_scene()",
            "",
        ]

        for comp in structure.get("components", []):
            name = comp.get("name", "part")
            dims = comp.get("dimensions", [1.0, 1.0, 1.0])
            pos = comp.get("position", [0.0, 0.0, 0.0])

            # Безопасное создание куба
            code.extend(
                [
                    f"bpy.ops.mesh.primitive_cube_add(location={pos})",
                    "obj = bpy.context.active_object",
                    f"obj.name = '{name}'",
                    f"obj.scale = ({dims[0]}, {dims[1]}, {dims[2]})",
                    "",
                ]
            )

        code.append("print('✅ Generation complete')")
        return "\n".join(code)

    def _create_component_code(self, component: Dict, index: int) -> List[str]:
        """Генерирует код для одного компонента"""
        comp_type = component["type"]
        position = component.get("position", [0, 0, 0])
        dimensions = component.get("dimensions", [1, 1, 1])
        material = component.get("material", "metal")

        code = []

        if comp_type == "extruded":
            # Лезвие меша
            code.extend(
                [
                    f"# Лезвие {index}",
                    "bm = bmesh.new()",
                    "# Вершины для лезвия",
                    "verts = [",
                    "    Vector((-0.05, 0, 0)), Vector((0.05, 0, 0)),",
                    "    Vector((-0.08, 0, 0.5)), Vector((0.08, 0, 0.5)),",
                    "    Vector((-0.05, 0, 1.0)), Vector((0.05, 0, 1.0)),",
                    "    Vector((-0.02, 0, 1.2)), Vector((0.02, 0, 1.2))",
                    "]",
                    "",
                    "# Создание faces",
                    "for v in verts:",
                    "    bm.verts.new(v)",
                    "bm.verts.ensure_lookup_table()",
                    "",
                    "# Полигоны",
                    "bm.faces.new([bm.verts[0], bm.verts[2], bm.verts[3], bm.verts[1]])",
                    "bm.faces.new([bm.verts[2], bm.verts[4], bm.verts[5], bm.verts[3]])",
                    "bm.faces.new([bm.verts[4], bm.verts[6], bm.verts[7], bm.verts[5]])",
                    "",
                    "# Создание меша",
                    f"mesh_{index} = bpy.data.meshes.new('blade_{index}')",
                    "bm.to_mesh(mesh_{index})",
                    "bm.free()",
                    f"obj_{index} = bpy.data.objects.new('blade_{index}', mesh_{index})",
                    "bpy.context.collection.objects.link(obj_{index})",
                    f"obj_{index}.location = {position}",
                    f"obj_{index}.data.materials.append(mat_{material})",
                    "",
                ]
            )

        elif comp_type == "cylinder":
            # Рукоять
            code.extend(
                [
                    f"# Рукоять {index}",
                    f"bpy.ops.mesh.primitive_cylinder_add(",
                    f"    vertices=32, radius={dimensions[0]}, depth={dimensions[2]},",
                    f"    location={position}",
                    f")",
                    f"obj_{index} = bpy.context.active_object",
                    f"obj_{index}.name = 'handle_{index}'",
                    f"obj_{index}.data.materials.append(mat_{material})",
                    "bpy.ops.object.shade_smooth()",
                    "",
                ]
            )

        elif comp_type == "box":
            # Гарда
            code.extend(
                [
                    f"# Гарда {index}",
                    f"bpy.ops.mesh.primitive_cube_add(size=1, location={position})",
                    f"obj_{index} = bpy.context.active_object",
                    f"obj_{index}.name = 'guard_{index}'",
                    f"bpy.ops.transform.resize(value={dimensions})",
                    f"obj_{index}.data.materials.append(mat_{material})",
                    "",
                ]
            )

        return code
