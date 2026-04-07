import ast
import logging
from typing import Dict, Any


class BlenderAPIHelper:
    """
    Интеллектуальный мост между LLM и Blender API.
    Очищает, валидирует и подготавливает код к исполнению.
    Версия: 2.4 (Hotfix: Removal of missing_elements)
    """

    def __init__(self):
        self.logger = logging.getLogger("ChronosHelper")
        # Запрещенные паттерны, которые часто галлюцинируют модели
        self.BANNED_PATTERNS = {
            "plt.": "Используй только bpy для визуализации, а не matplotlib.",
            "input(": "Интерактивный ввод заблокирован в headless-режиме.",
            "os.exit": "Нельзя закрывать процесс Blender изнутри скрипта.",
            "cv2": "OpenCV не установлен в стандартном Python Blender.",
        }

    def get_gold_standard_template(self) -> str:
        """
        Возвращает эталонный шаблон кода.
        Этот текст должен быть частью системного промпта для LLM.
        """
        return """
# --- CHRONOS TEMPLATE START ---
import bpy
import bmesh
import math
from mathutils import Vector, Matrix

def create_geometry(bm):
    # ТВОЙ КОД ЗДЕСЬ. Используй bmesh операции.
    # Пример: bmesh.ops.create_cube(bm, size=1.0)
    pass

# --- CHRONOS TEMPLATE END ---
        """

    def _extract_pure_code(self, text: str) -> str:
        if "```" in text:
            # Ищем текст между первыми ```python и последними ```
            parts = text.split("```")
            for part in parts:
                if "import " in part or "bmesh" in part:
                    return part.replace("python", "").strip()
        return text.strip()

    def validate_and_fix_syntax(self, raw_code: str) -> Dict[str, Any]:
        """Проверка кода и подготовка отчета для Оркестратора."""
        report = {"is_valid": True, "errors": [], "suggestions": [], "cleaned_code": ""}

        # 1. Извлечение
        code = self._extract_pure_code(raw_code)

        if not code:
            report["is_valid"] = False
            report["errors"].append("LLM returned no executable code.")
            return report

        # 2. Синтаксический анализ
        try:
            ast.parse(code)
            report["cleaned_code"] = code
        except SyntaxError as e:
            report["is_valid"] = False
            report["errors"].append(f"Syntax Error at line {e.lineno}: {e.msg}")
            return report

        # 3. Проверка запрещенных паттернов
        for pattern, replacement in self.BANNED_PATTERNS.items():
            if pattern in code:
                report["suggestions"].append(f"Замечено '{pattern}': {replacement}")

        return report

    def wrap_in_chronos_context(
        self, logic_code: str, asset_id: str = "GEN_ASSET"
    ) -> str:
        """Оборачивает логику в безопасную функцию с инициализацией bmesh."""
        # Подготовка отступов (8 пробелов)
        indented_logic = "\n".join(
            [
                f"        {line}" if line.strip() else ""
                for line in logic_code.strip().split("\n")
            ]
        )

        return f"""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

def execute_chronos_generation():
    print("🛠 Chronos: Start generation of {asset_id}")
    
    # Очистка старого объекта
    if "{asset_id}" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["{asset_id}"], do_unlink=True)

    mesh_data = bpy.data.meshes.new("{asset_id}_mesh")
    obj = bpy.data.objects.new("{asset_id}", mesh_data)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    try:
{indented_logic}
        
        # Финализация
        bm.to_mesh(mesh_data)
        bm.free()
        bpy.context.view_layer.update()
        print("✅ Chronos: {asset_id} successfully created.")
        
    except Exception as e:
        if bm: bm.free()
        print(f"❌ Execution Error: {{str(e)}}")
        raise e

if __name__ == "__main__":
    execute_chronos_generation()
"""

    def get_api_hint(self, context: str) -> str:
        """Подсказки для системного промпта."""
        hints = {
            "prop": "Use bmesh.ops.create_cube for basic shapes. Ensure you use bm.verts.ensure_lookup_table() before accessing indices.",
            "weapon": "Focus on thin extruded bmesh regions for blades.",
            "architecture": "Use nested loops for repeating elements like steps or windows.",
        }
        return hints.get(context, "Use bmesh API for geometry generation.")
