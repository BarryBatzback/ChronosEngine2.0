"""
Сервис для ретопологии и оптимизации сетки
"""


class RetopologyService:
    """Оптимизация 3D моделей для игр"""

    def generate_retopology_code(
        self,
        target_polycount: int = 10000,
        use_decimate: bool = True,
        use_remesh: bool = False,
    ) -> str:
        """
        Генерация кода для оптимизации сетки
        """
        code_lines = [
            "import bpy",
            "",
            "# ============================================================",
            "# ОПТИМИЗАЦИЯ СЕТКИ",
            "# ============================================================",
            "",
            "def optimize_mesh(obj, target_polycount):",
            '    """Оптимизация меша под целевое количество полигонов"""',
            "    if obj.type != 'MESH':",
            "        return",
            "",
            "    current_faces = len(obj.data.polygons)",
            f"    target_faces = {target_polycount}",
            "",
            "    if current_faces <= target_faces:",
            "        print(f'Mesh already optimized: {{current_faces}} faces')",
            "        return",
            "",
            "    # Рассчитываем коэффициент уменьшения",
            "    ratio = target_faces / current_faces",
            "    print(f'Reducing from {{current_faces}} to {{target_faces}} faces (ratio: {{ratio:.2f}})')",
            "",
            "    # Добавляем Decimate модификатор",
            "    mod = obj.modifiers.new(name='Optimize', type='DECIMATE')",
            "    mod.ratio = ratio",
            "    mod.use_collapse_triangulate = True",
            "",
            "    # Применяем модификатор",
            "    bpy.context.view_layer.objects.active = obj",
            "    bpy.ops.object.modifier_apply(modifier='Optimize')",
            "",
            "    print(f'✅ Optimized: {{len(obj.data.polygons)}} faces')",
            "",
        ]

        if use_decimate:
            code_lines.extend(
                [
                    "# Применяем оптимизацию ко всем выделенным объектам",
                    "for obj in bpy.context.selected_objects:",
                    "    optimize_mesh(obj, 10000)",
                ]
            )

        if use_remesh:
            code_lines.extend(
                [
                    "",
                    "# Альтернатива: Remesh модификатор для органических форм",
                    "def apply_remesh(obj, voxel_size=0.05):",
                    "    mod = obj.modifiers.new(name='Remesh', type='REMESH')",
                    "    mod.mode = 'VOXEL'",
                    "    mod.voxel_size = voxel_size",
                    "    bpy.context.view_layer.objects.active = obj",
                    "    bpy.ops.object.modifier_apply(modifier='Remesh')",
                ]
            )

        return "\n".join(code_lines)

    def generate_lod_code(self, levels: int = 3) -> str:
        """
        Генерация уровней детализации (LOD)
        """
        code_lines = [
            "import bpy",
            "",
            "# ============================================================",
            f"# ГЕНЕРАЦИЯ LOD ({levels} уровней)",
            "# ============================================================",
            "",
            "def generate_lods(obj, levels):",
            '    """Создание уровней детализации"""',
            "    if obj.type != 'MESH':",
            "        return",
            "",
            "    original_name = obj.name",
            "    current_faces = len(obj.data.polygons)",
            "",
            "    for i in range(1, levels + 1):",
            "        # Копируем объект",
            "        obj_copy = obj.copy()",
            "        obj_copy.data = obj.data.copy()",
            "        obj_copy.name = f'{{original_name}}_LOD{{i}}'",
            "        bpy.context.collection.objects.link(obj_copy)",
            "",
            "        # Рассчитываем коэффициент",
            "        ratio = 1.0 / (i * 2)",
            "        target_faces = int(current_faces * ratio)",
            "",
            "        # Добавляем Decimate",
            "        mod = obj_copy.modifiers.new(name=f'LOD{{i}}_Decimate', type='DECIMATE')",
            "        mod.ratio = ratio",
            "",
            "        print(f'  LOD{i}: {{target_faces}} faces (ratio: {{ratio:.2f}})')",
            "",
            "    print(f'✅ Generated {levels} LOD levels for {{original_name}}')",
            "",
            "# Генерация LOD для выделенных объектов",
            "for obj in bpy.context.selected_objects:",
            f"    generate_lods(obj, {levels})",
        ]

        return "\n".join(code_lines)
