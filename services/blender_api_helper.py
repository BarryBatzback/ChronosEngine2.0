import ast
import logging
from typing import Dict, List, Any

class BlenderAPIHelper:
    def __init__(self):
        # Список запрещенных/устаревших методов для Blender 4.2+ / 5.1
        self.forbidden_patterns = {
            "bpy.ops.mesh.primitive_cube_add": "Используйте bmesh.ops.create_cube для гибкости",
            "bpy.data.textures": "Используйте Shader Nodes через material.use_nodes",
            "mesh.tessface": "Используйте mesh.polygons (API устарел с версии 2.8)"
        }

    def validate_syntax(self, code: str) -> bool:
        """Проверяет код на наличие синтаксических ошибок перед отправкой в Blender"""
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            logging.error(f"Syntax error in generated code: {e}")
            return False

    def get_improvement_suggestions(self, code: str) -> List[str]:
        """Ищет плохие паттерны в коде и выдает рекомендации"""
        suggestions = []
        for pattern, reason in self.forbidden_patterns.items():
            if pattern in code:
                suggestions.append(f"Внимание: Найдено '{pattern}'. {reason}")
        return suggestions

    def wrap_in_boilerplate(self, logic_code: str) -> str:
        """Оборачивает логику в безопасный контекст BMesh"""
        return f"""
import bpy
import bmesh
from mathutils import Vector, Matrix

def execute_logic():
    # Создаем временный меш
    mesh = bpy.data.meshes.new("GeneratedMesh")
    obj = bpy.data.objects.new("GeneratedObject", mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    try:
        # Вставка сгенерированного кода
{self._indent_code(logic_code)}
        
        # Финализация
        bm.to_mesh(mesh)
        bm.free()
        bpy.context.view_layer.update()
    except Exception as e:
        print(f"Error during execution: {{e}}")
        bm.free()

execute_logic()
"""

    def _indent_code(self, code: str, spaces: int = 8) -> str:
        return "\n".join(" " * spaces + line for line in code.splitlines())