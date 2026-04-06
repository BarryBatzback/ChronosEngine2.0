"""
Интеллектуальный помощник Blender API для Chronos Engine 2.0.
Отвечает за очистку, валидацию и безопасное выполнение кода генерации.
"""

import re
import ast
import logging
import time
from typing import Dict, Any, List, Tuple, Optional

# Настройка логгера (используем существующий в проекте или стандартный)
try:
    from loguru import logger
except ImportError:
    logger = logging.getLogger(__name__)

print("⚙️ BlenderAPIHelper: Loading Production Version 2.4 (Suggestions & Bugfixes)...")

class BlenderAPIHelper:
    """
    Валидация, исправление и обертка кода для безопасного выполнения в Blender.
    """
    
    def __init__(self):
        # Запрещенные паттерны (типичные ошибки LLM)
        self.BANNED_PATTERNS = {
            "bpy.ops.mesh.primitive_": "Используйте bmesh.ops для процедурной генерации.",
            "bpy.data.textures": "Используйте Shader Nodes.",
            "mesh.tessface": "Устарело. Используйте mesh.polygons.",
            "bpy.ops.object.mode_set": "Избегайте переключения режимов."
        }
        
        self.ALLOWED_IMPORTS = {
            "bpy", "bmesh", "mathutils", "math", "random", "json", 
            "typing", "collections", "itertools"
        }

    def get_api_hint(self, context: str) -> str:
        """
        Возвращает контекстную подсказку для LLM.
        """
        hints = {
            "palisade": (
                "Для генерации частокола:\n"
                "1. Используйте bmesh.ops.create_cone или create_cube для сегментов.\n"
                "2. Для заострения переместите верхние вершины в одну точку или используйте конус.\n"
                "3. Обязательно используйте random.uniform для вариативности высоты.\n"
                "4. Расставляйте объекты вдоль оси X с шагом, равным диаметру бревна."
            ),
            "bmesh_general": (
                "Используйте bmesh.new(), затем bm.to_mesh() и bm.free() в конце.\n"
                "Вызывайте bm.verts.ensure_lookup_table() перед доступом к индексам."
            )
        }
        return hints.get(context, hints["bmesh_general"])

    def _extract_pure_code(self, raw_response: str) -> str:
        """Извлекает Python код из markdown блоков ИИ."""
        patterns = [
            r'```python\n(.*?)```',
            r'```\n(.*?)```',
            r'```(.*?)```'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, raw_response, re.DOTALL)
            if match:
                code = match.group(1).strip()
                # Очистка от лишних отступов
                lines = code.split('\n')
                if lines:
                    first_line = next((l for l in lines if l.strip()), "")
                    indent = len(first_line) - len(first_line.lstrip())
                    if indent > 0:
                        code = '\n'.join(l[indent:] if len(l) >= indent else l for l in lines)
                return code
        
        return raw_response.strip()

    def _validate_python_syntax(self, code: str) -> Tuple[bool, List[str]]:
        """Проверка синтаксиса Python через AST."""
        errors = []
        try:
            ast.parse(code)
            return True, []
        except SyntaxError as e:
            errors.append(f"SYNTAX ERROR [Line {e.lineno}]: {e.msg}")
            return False, errors

    def _fix_syntax_errors(self, code: str, errors: List[str]) -> str:
        """Попытка автоматического исправления простых ошибок."""
        lines = code.split('\n')
        for error in errors:
            match = re.search(r'line (\d+)', error)
            if match:
                idx = int(match.group(1)) - 1
                if 0 <= idx < len(lines):
                    line = lines[idx]
                    for opening, closing in [('(', ')'), ('[', ']'), ('{', '}')]:
                        if line.count(opening) > line.count(closing):
                            lines[idx] = line + closing
        return '\n'.join(lines)

    def validate_and_fix_syntax(self, raw_code: str) -> Dict[str, Any]:
        """
        Основной метод валидации кода. 
        Теперь включает ключ 'suggestions' для предотвращения KeyError в Orchestrator.
        """
        report = {
            "is_valid": True, 
            "errors": [], 
            "suggestions": [], 
            "cleaned_code": ""
        }
        
        # 1. Извлечение
        code = self._extract_pure_code(raw_code)
        
        # 2. Проверка синтаксиса
        is_valid, syntax_errors = self._validate_python_syntax(code)
        if not is_valid:
            code = self._fix_syntax_errors(code, syntax_errors)
            # Повторная попытка после исправления
            is_valid, syntax_errors = self._validate_python_syntax(code)
            if not is_valid:
                report["is_valid"] = False
                report["errors"].extend(syntax_errors)
                report["suggestions"].append("Проверьте закрывающие скобки и кавычки в указанных строках.")

        # 3. Поиск запрещенных паттернов
        for pattern, msg in self.BANNED_PATTERNS.items():
            if pattern in code:
                warn_msg = f"Найден запрещенный паттерн: {pattern}"
                report["errors"].append(warn_msg)
                report["suggestions"].append(msg)

        report["cleaned_code"] = code
        return report

    def wrap_in_chronos_context(self, logic_code: str, asset_id: str = "GEN_ASSET") -> str:
        """Оборачивает логику в изолированную функцию."""
        indented_logic = '\n'.join(['        ' + line for line in logic_code.strip().split('\n')])
        
        return f'''
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

def execute_chronos_generation():
    """Автоматически сгенерировано Chronos Engine"""
    print("🚀 Starting generation of: {asset_id}")
    
    if "{asset_id}" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["{asset_id}"], do_unlink=True)

    mesh_data = bpy.data.meshes.new("{asset_id}_mesh")
    obj = bpy.data.objects.new("{asset_id}", mesh_data)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    try:
{indented_logic}
        bm.to_mesh(mesh_data)
        bm.free()
        bpy.context.view_layer.update()
        print("✅ {asset_id} successfully created.")
    except Exception as e:
        if bm: bm.free()
        print(f"❌ Generation Error: {{str(e)}}")
        import traceback
        traceback.print_exc()
        raise e

if __name__ == "__main__":
    execute_chronos_generation()
'''

    def validate_and_wrap_code(self, raw_llm_response: str, asset_id: str) -> str:
        """Полный цикл обработки кода."""
        validation = self.validate_and_fix_syntax(raw_llm_response)
        return self.wrap_in_chronos_context(validation["cleaned_code"], asset_id)