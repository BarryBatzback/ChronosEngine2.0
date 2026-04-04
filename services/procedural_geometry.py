"""
Процедурная генерация кода на основе семантической структуры
"""

import json
from typing import Dict, Any, List
from loguru import logger


class ProceduralGeometryGenerator:
    """Генератор кода Blender на основе структуры компонентов"""

    def generate_code(self, structure: Dict[str, Any]) -> str:
        """
        Генерация Python кода для Blender на основе структуры
        """
        components = structure.get('components', [])
        materials = structure.get('materials', {})
        modifiers = structure.get('modifiers', [])
        connections = structure.get('connections', [])

        code_lines = [
            "import bpy",
            "import bmesh",
            "from mathutils import Vector, Matrix",
            "from math import radians",
            "",
            "# ============================================================",
            "# ОЧИСТКА СЦЕНЫ",
            "# ============================================================",
            "bpy.ops.object.select_all(action='SELECT')",
            "bpy.ops.object.delete(use_global=False)",
            "",
            "# ============================================================",
            "# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ",
            "# ============================================================",
            "",
            "def create_box(name, width, height, depth, position, rotation=None):",
            "    \"\"\"Создание box\"\"\"",
            "    bpy.ops.mesh.primitive_cube_add(size=1, location=position)",
            "    obj = bpy.context.active_object",
            "    obj.scale = (width, height, depth)",
            "    obj.name = name",
            "    if rotation:",
            "        obj.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))",
            "    return obj",
            "",
            "def create_cylinder(name, radius, height, position, rotation=None):",
            "    \"\"\"Создание цилиндра\"\"\"",
            "    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, location=position)",
            "    obj = bpy.context.active_object",
            "    obj.name = name",
            "    if rotation:",
            "        obj.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))",
            "    return obj",
            "",
            "def create_sphere(name, radius, position):",
            "    \"\"\"Создание сферы\"\"\"",
            "    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=position)",
            "    obj = bpy.context.active_object",
            "    obj.name = name",
            "    return obj",
            "",
            "def create_cone(name, radius, height, position):",
            "    \"\"\"Создание конуса\"\"\"",
            "    bpy.ops.mesh.primitive_cone_add(radius1=radius, depth=height, location=position)",
            "    obj = bpy.context.active_object",
            "    obj.name = name",
            "    return obj",
            "",
            "def create_torus(name, radius, radius2, position):",
            "    \"\"\"Создание тора\"\"\"",
            "    bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=radius2, location=position)",
            "    obj = bpy.context.active_object",
            "    obj.name = name",
            "    return obj",
            "",
            "def create_extruded_shape(name, points, height, position):",
            "    \"\"\"Создание экструдированной формы (для лезвий)\"\"\"",
            "    bm = bmesh.new()",
            "    verts = []",
            f"    for p in {points}:",
            "        verts.append(bm.verts.new((p[0], p[1], 0)))",
            "    bm.verts.ensure_lookup_table()",
            "    for i in range(len(verts)):",
            "        bm.edges.new((verts[i], verts[(i+1) % len(verts)]))",
            "    bmesh.ops.extrude_edge_only(bm, edges=bm.edges)",
            f"    bmesh.ops.translate(bm, vec=(0,0,{height}), verts=bm.verts)",
            "    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)",
            "    mesh = bpy.data.meshes.new(name)",
            "    bm.to_mesh(mesh)",
            "    bm.free()",
            "    obj = bpy.data.objects.new(name, mesh)",
            "    bpy.context.collection.objects.link(obj)",
            f"    obj.location = {position}",
            "    return obj",
            "",
            "# ============================================================",
            "# ФУНКЦИИ СОЗДАНИЯ МАТЕРИАЛОВ",
            "# ============================================================",
            "",
            "def create_material(name, mat_type):",
            "    \"\"\"Создание PBR материала\"\"\"",
            "    mat = bpy.data.materials.new(name=name)",
            "    mat.use_nodes = True",
            "    nodes = mat.node_tree.nodes",
            "    links = mat.node_tree.links",
            "    nodes.clear()",
            "",
            "    output = nodes.new(type='ShaderNodeOutputMaterial')",
            "    output.location = (400, 0)",
            "",
            "    principled = nodes.new(type='ShaderNodeBsdfPrincipled')",
            "    principled.location = (200, 0)",
            "",
            "    if mat_type == 'wood':",
            "        principled.inputs['Base Color'].default_value = (0.55, 0.38, 0.22, 1.0)",
            "        principled.inputs['Roughness'].default_value = 0.6",
            "        principled.inputs['Specular'].default_value = 0.3",
            "        # Добавляем текстуру дерева",
            "        noise = nodes.new(type='ShaderNodeTexNoise')",
            "        noise.location = (-200, 200)",
            "        noise.inputs['Scale'].default_value = 5.0",
            "        color_ramp = nodes.new(type='ShaderNodeValToRGB')",
            "        color_ramp.location = (0, 200)",
            "        color_ramp.color_ramp.elements[0].color = (0.35, 0.22, 0.12, 1.0)",
            "        color_ramp.color_ramp.elements[1].color = (0.55, 0.38, 0.22, 1.0)",
            "        links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])",
            "        links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])",
            "",
            "    elif mat_type == 'metal':",
            "        principled.inputs['Metallic'].default_value = 1.0",
            "        principled.inputs['Roughness'].default_value = 0.3",
            "        principled.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)",
            "",
            "    elif mat_type == 'red':",
            "        principled.inputs['Base Color'].default_value = (1.0, 0.0, 0.0, 1.0)",
            "",
            "    elif mat_type == 'blue':",
            "        principled.inputs['Base Color'].default_value = (0.0, 0.0, 1.0, 1.0)",
            "",
            "    elif mat_type == 'green':",
            "        principled.inputs['Base Color'].default_value = (0.0, 0.5, 0.0, 1.0)",
            "",
            "    elif mat_type == 'glass':",
            "        principled.inputs['Transmission'].default_value = 1.0",
            "        principled.inputs['Roughness'].default_value = 0.1",
            "        principled.inputs['IOR'].default_value = 1.45",
            "",
            "    else:",
            "        principled.inputs['Base Color'].default_value = (0.5, 0.5, 0.5, 1.0)",
            "",
            "    links.new(principled.outputs['BSDF'], output.inputs['Surface'])",
            "    return mat",
            "",
            "# ============================================================",
            "# ФУНКЦИИ ДОБАВЛЕНИЯ МОДИФИКАТОРОВ",
            "# ============================================================",
            "",
            "def add_modifiers(obj, modifiers_list):",
            "    \"\"\"Добавление модификаторов\"\"\"",
            "    for mod_name in modifiers_list:",
            "        if mod_name == 'bevel':",
            "            mod = obj.modifiers.new(name='Bevel', type='BEVEL')",
            "            mod.width = 0.02",
            "            mod.segments = 2",
            "        elif mod_name == 'subdivision':",
            "            mod = obj.modifiers.new(name='Subdivision', type='SUBSURF')",
            "            mod.levels = 1",
            "            mod.render_levels = 2",
            "        elif mod_name == 'array':",
            "            mod = obj.modifiers.new(name='Array', type='ARRAY')",
            "            mod.count = 3",
            "            mod.relative_offset_displace = (1.5, 0, 0)",
            "",
            "# ============================================================",
            "# СОЗДАНИЕ КОМПОНЕНТОВ",
            "# ============================================================",
            ""
        ]

        # Словарь для хранения созданных объектов
        created_objects = {}

        # Генерируем код для каждого компонента
        for comp in components:
            name = comp.get('name')
            comp_type = comp.get('type')
            position = comp.get('position', [0, 0, 0])
            rotation = comp.get('rotation', [0, 0, 0])

            code_lines.append(f"# Создание {name}")

            if comp_type == 'box':
                width = comp.get('width', 1.0)
                height = comp.get('height', 1.0)
                depth = comp.get('depth', 1.0)
                code_lines.append(f"obj_{name} = create_box('{name}', {width}, {height}, {depth}, {position}, {rotation})")

            elif comp_type == 'cylinder':
                radius = comp.get('radius', 0.5)
                height = comp.get('height', 1.0)
                code_lines.append(f"obj_{name} = create_cylinder('{name}', {radius}, {height}, {position}, {rotation})")

            elif comp_type == 'sphere':
                radius = comp.get('radius', 0.5)
                code_lines.append(f"obj_{name} = create_sphere('{name}', {radius}, {position})")

            elif comp_type == 'cone':
                radius = comp.get('radius', 0.5)
                height = comp.get('height', 1.0)
                code_lines.append(f"obj_{name} = create_cone('{name}', {radius}, {height}, {position})")

            elif comp_type == 'torus':
                radius = comp.get('radius', 0.5)
                radius2 = comp.get('radius2', 0.1)
                code_lines.append(f"obj_{name} = create_torus('{name}', {radius}, {radius2}, {position})")

            elif comp_type == 'extruded_shape':
                points = comp.get('points', [[0, 0], [0.1, 0.5], [0, 1], [-0.1, 0.5]])  # Дефолтное значение
                height = comp.get('height', 2.0)
                code_lines.append(f"obj_{name} = create_extruded_shape('{name}', {points}, {height}, {position})")

            created_objects[name] = f"obj_{name}"
            code_lines.append("")

        # Применяем материалы
        code_lines.append("# ============================================================")
        code_lines.append("# ПРИМЕНЕНИЕ МАТЕРИАЛОВ")
        code_lines.append("# ============================================================")
        code_lines.append("")

        default_material = materials.get('default', 'wood')
        for comp in components:
            name = comp.get('name')
            mat_type = materials.get(name, default_material)
            code_lines.append(f"if obj_{name}:")
            code_lines.append(f"    mat = create_material('{name}_mat', '{mat_type}')")
            code_lines.append(f"    if len(obj_{name}.data.materials) == 0:")
            code_lines.append(f"        obj_{name}.data.materials.append(mat)")
            code_lines.append(f"    else:")
            code_lines.append(f"        obj_{name}.data.materials[0] = mat")
            code_lines.append("")

        # Применяем модификаторы
        if modifiers:
            code_lines.append("# ============================================================")
            code_lines.append("# ПРИМЕНЕНИЕ МОДИФИКАТОРОВ")
            code_lines.append("# ============================================================")
            code_lines.append("")
            for comp in components:
                name = comp.get('name')
                code_lines.append(f"if obj_{name}:")
                code_lines.append(f"    add_modifiers(obj_{name}, {modifiers})")
            code_lines.append("")

        # Parent связи
        if connections:
            code_lines.append("# ============================================================")
            code_lines.append("# СОЗДАНИЕ ИЕРАРХИИ")
            code_lines.append("# ============================================================")
            code_lines.append("")
            for conn in connections:
                parent = conn.get('from')
                child = conn.get('to')
                code_lines.append(f"if obj_{parent} and obj_{child}:")
                code_lines.append(f"    obj_{child}.parent = obj_{parent}")
            code_lines.append("")

        # Финальное сообщение
        code_lines.append("# ============================================================")
        code_lines.append("# ЗАВЕРШЕНИЕ")
        code_lines.append("# ============================================================")
        code_lines.append("print('✅ Object created successfully!')")
        code_lines.append(f"print('📊 Components: {len(components)}')")

        return '\n'.join(code_lines)