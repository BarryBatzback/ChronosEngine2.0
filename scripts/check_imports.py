# scripts/check_imports.py (исправленная версия)
import sys
from pathlib import Path

# Добавляем корневую директорию
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

try:
    from services.component_library import ComponentLibrary
    print("✅ ComponentLibrary import: SUCCESS")
    
    lib = ComponentLibrary()
    print("✅ ComponentLibrary instantiation: SUCCESS")
    print(f"✅ Assets detection: {lib.has_assets()}")
    
except ImportError as e:
    print("❌ ComponentLibrary import failed:", e)
    print("Python path:")
    for p in sys.path:
        print(f"  {p}")
        
except Exception as e:
    print("❌ Other error:", e)
