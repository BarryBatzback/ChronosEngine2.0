# setup_environment.py
import sys
from pathlib import Path

def setup_environment():
    """Настраивает окружение для всех модулей"""
    # Добавляем корневую директорию
    root_dir = Path(__file__).parent
    sys.path.insert(0, str(root_dir))
    
    print(f"✅ Root directory added to path: {root_dir}")
    print("Python path now:")
    for i, p in enumerate(sys.path[:5]):  # Покажем первые 5 путей
        print(f"  {i+1}. {p}")

# Применяем сразу
setup_environment()
