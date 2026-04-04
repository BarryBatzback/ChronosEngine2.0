import ast
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

class BlenderAPIHelper:
    """
    Интеллектуальный помощник Blender API.
    Гарантирует чистоту кода, отсутствие deprecated методов и соблюдение логики Chronos Engine.
    """
    
    def __init__(self):
        # Запрещенные паттерны, которые часто путает LLM
        self.BANNED_PATTERNS = {
            "bpy.ops.mesh.primitive_": "Используйте bmesh.ops для процедурной генерации.",
            "bpy.data.textures": "Используйте Shader Nodes (principled_bsdf) через bpy.data.materials.",
            "mesh.tessface": "Устарело. Используйте mesh.polygons или bmesh.",
            "select_all(action='DESELECT')": "Старайтесь избегать операторов выделения, работайте с объектами напрямую."
        }

    def validate_and_fix_syntax(self, code: str) -> Dict[str, Any]:
        """Полная проверка кода на ошибки и плохие практики."""
        report = {"is_valid": True, "errors": [], "suggestions": []}
        
        # 1. Синтаксический анализ
        try:
            ast.parse(code)
        except SyntaxError as e:
            report["is_valid"] = False
            report["errors"].append(f"Syntax Error at line {e.lineno}: {e.msg}")
            return report

        # 2. Проверка на запрещенные паттерны
        for pattern, replacement in self.BANNED_PATTERNS.items():
            if pattern in code:
                report["suggestions"].append(f"Найдено '{pattern}': {replacement}")

        return report

    def wrap_in_chronos_context(self, logic_code: str, asset_id: str = "GEN_ASSET") -> str:
        """
        Оборачивает «сырой» код от ИИ в безопасную среду исполнения.
        Автоматически добавляет импорты и обработку BMesh.
        """
        # Убираем лишние отступы у входящего кода, если они есть
        clean_logic = self._prepare_logic(logic_code)
        
        return f'''
import bpy
import bmesh
import math
from mathutils import Vector, Matrix

def execute_chronos_generation():
    # Инициализация чистого меша
    mesh_data = bpy.data.meshes.new("{asset_id}_mesh")
    obj = bpy.data.objects.new("{asset_id}", mesh_data)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    try:
        # --- НАЧАЛО ГЕНЕРИРУЕМОЙ ЛОГИКИ ---
{clean_logic}
        # --- КОНЕЦ ГЕНЕРИРУЕМОЙ ЛОГИКИ ---

        # Финализация меша
        bm.to_mesh(mesh_data)
        bm.free()
        
        # Обновление сцены
        bpy.context.view_layer.update()
        print("✅ Chronos Engine: Asset {asset_id} generated successfully")
        
    except Exception as e:
        if bm: bm.free()
        print(f"❌ Chronos Engine Error: {{str(e)}}")
        raise e

if __name__ == "__main__":
    execute_chronos_generation()
'''

    def _prepare_logic(self, code: str) -> str:
        """Форматирует код для вставки в функцию с правильными отступами."""
        lines = code.strip().split('\n')
        return '\n'.join(['        ' + line for line in lines])

    def get_api_hint(self, context: str) -> str:
        """Выдает подсказку для LLM, как писать код для конкретной задачи."""
        hints = {
            "blade": "Используй bmesh.ops.create_vert для острия и bmesh.ops.extrude_face_region для дола.",
            "material": "Для металлов 9-го века (iron/steel) ставь Metallic=1.0 и Roughness > 0.3.",
            "handle": "Используй bmesh.ops.create_cone для основы рукояти."
        }
        return hints.get(context, "Используй bmesh для всех операций с геометрией.")