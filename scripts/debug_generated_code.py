# scripts/debug_generated_code.py (исправляем)
import sys
from pathlib import Path

# Добавляем корневой путь
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from services.component_library import ComponentLibrary
from services.semantic_analyzer import SemanticAnalyzer

def debug_generated_code():
    # Создаем компоненты
    lib = ComponentLibrary()
    analyzer = SemanticAnalyzer()
    
    # Анализируем запрос (синхронно!)
    structure = analyzer._analyze_sync("create a fantasy sword")
    print("📐 Structure:", structure)
    
    # Генерируем код
    code_lines = [
        "import bpy",
        "from pathlib import Path",
        "",
        "# Очистка сцены",
        "bpy.ops.object.select_all(action='SELECT')",
        "bpy.ops.object.delete(use_global=False, confirm=False)",
        ""
    ]
    
    # Добавляем импорт компонентов
    code_lines.append(lib.import_component_code('sword', 'blade', 'basic', [0, 0, 0.6]))
    code_lines.append(lib.import_component_code('sword', 'guard', 'basic', [0, 0, 0.1]))
    code_lines.append(lib.import_component_code('sword', 'handle', 'basic', [0, 0, -0.3]))
    
    # Финализация (без emoji символов)
    code_lines.extend([
        "",
        "# Финализация",
        "bpy.ops.object.select_all(action='SELECT')",
        "bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')",
        "bpy.ops.object.select_all(action='DESELECT')",
        "",
        "print('Me4 sozdan iz assetov!')",  # Без emoji
    ])
    
    full_code = '\n'.join(code_lines)
    
    print("🔍 Generated code:")
    print("=" * 50)
    print(full_code)
    print("=" * 50)
    
    # Сохраним для тестирования (с правильной кодировкой)
    with open("debug_asset_code.py", "w", encoding="utf-8") as f:
        f.write(full_code)
    
    return full_code

if __name__ == "__main__":
    debug_generated_code()
