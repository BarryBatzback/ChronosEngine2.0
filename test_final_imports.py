# test_final_imports.py
import sys
from pathlib import Path

# Правильная настройка путей
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

print("=" * 50)
print("FINAL IMPORT TEST")
print("=" * 50)

try:
    from services.component_library import ComponentLibrary
    print("✅ services.component_library: SUCCESS")
    
    from agents.geometry_agent import GeometryAgent
    print("✅ agents.geometry_agent: SUCCESS")
    
    from core.orchestrator import Orchestrator
    print("✅ core.orchestrator: SUCCESS")
    
    # Тестируем создание объектов
    lib = ComponentLibrary()
    print(f"✅ ComponentLibrary instance: {lib.has_assets()}")
    
    print("=" * 50)
    print("🎉 ALL IMPORTS WORKING!")
    print("=" * 50)
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("\nCurrent Python path:")
    for i, p in enumerate(sys.path):
        print(f"  {i+1}. {p}")
        
except Exception as e:
    print(f"❌ Other error: {e}")
