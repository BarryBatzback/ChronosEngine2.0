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

    def _extract_pure_code(self, raw_response: str) -> str:
        """
        Извлекает основной блок кода Python из ответа LLM и очищает его
        от дублирующих импортов и системного мусора.

        Args:
            raw_response: Сырой ответ от языковой модели

        Returns:
            Очищенный Python-код для выполнения
        """
        import re

        # Список импортов, которые уже есть в wrap_in_chronos_context
        # и которые не должны дублироваться в теле кода
        duplicate_imports = [
            r"^import\s+bpy\s*$",
            r"^import\s+bmesh\s*$",
            r"^from\s+bpy\s+import\s+.*$",
            r"^from\s+math\s+import\s+.*$",
            r"^import\s+math\s*$",
            r"^import\s+random\s*$",
        ]

        # 1. Поиск блоков кода в markdown: ```python, ```py, или просто ```
        # re.DOTALL позволяет .*? захватывать переносы строк
        pattern = r"```(?:python|py)?\s*\n(.*?)```"
        matches = re.findall(pattern, raw_response, re.DOTALL | re.IGNORECASE)

        if matches:
            # Берём самый длинный блок кода (мажоритарный выбор)
            code = max(matches, key=len).strip()
        else:
            # Fallback: если нет маркдаун-блоков, ищем код по наличию импортов
            lines = raw_response.split("\n")
            code_lines = []
            in_code = False
            for line in lines:
                stripped = line.strip()
                # Начинаем собирать код, если видим типичную Python-конструкцию
                if (
                    stripped.startswith("import ")
                    or stripped.startswith("from ")
                    or stripped.startswith("def ")
                    or stripped.startswith("class ")
                ):
                    in_code = True
                if (
                    in_code
                    and stripped
                    and not stripped.startswith("#")
                    and "```" not in stripped
                ):
                    code_lines.append(line)
            code = "\n".join(code_lines).strip() if code_lines else raw_response.strip()

        # 2. Удаляем дублирующие импорты, которые уже есть в контексте Chronos
        code_lines = code.split("\n")
        filtered_lines = []
        for line in code_lines:
            stripped = line.strip()
            # Пропускаем строки, которые совпадают с нашими "запрещёнными" импортами
            if any(re.match(pattern, stripped) for pattern in duplicate_imports):
                continue
            filtered_lines.append(line)

        code = "\n".join(filtered_lines)

        # 3. Удаляем лишние пустые строки в начале и конце
        return code.strip()

    def fix_escape_sequences(self, code: str) -> str:
        """
        Исправляет ошибку W605 (invalid escape sequence).
        Заменяет одиночные обратные слеши в строках на двойные, если это не спецсимволы.
        """
        # Ищем пути или спец-символы в кавычках, которые не экранированы
        return code.replace("\\", "\\\\").replace("\\\\\\\\", "\\\\")

    def validate_and_fix_syntax(self, raw_code: str) -> Dict[str, Any]:
        """
        Проверяет код на наличие синтаксических ошибок перед запуском.
        """
        report = {"is_valid": True, "errors": [], "cleaned_code": ""}

        # Сначала очищаем
        code = self._extract_pure_code(raw_code)
        # Исправляем слеши для Windows-путей
        code = self.fix_escape_sequences(code)

        try:
            ast.parse(code)
            report["cleaned_code"] = code
        except SyntaxError as e:
            report["is_valid"] = False
            report["errors"].append(f"Line {e.lineno}: {e.msg}")

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
