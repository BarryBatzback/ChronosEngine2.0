# test_simple_imports.py
import sys
from pathlib import Path

# Настраиваем пути
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

print("=" * 50)
print("SIMPLE IMPORT TEST")
print("=" * 50)

# Тестируем только основные импорты
try:
    from services.component_library import ComponentLibrary
    print("✅ ComponentLibrary: SUCCESS")
    
    lib = ComponentLibrary()
    print(f"✅ Assets detected: {lib.has_assets()}")
    
    from core.orchestrator import Orchestrator
    print("✅ Orchestrator: SUCCESS")
    
    print("=" * 50)
    print("🎉 BASIC IMPORTS WORKING!")
    print("=" * 50)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
