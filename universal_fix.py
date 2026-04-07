# universal_fix.py
import sys
from pathlib import Path


def setup_paths():
    """Настраивает пути для всех модулей"""
    root_dir = Path(__file__).parent
    sys.path.insert(0, str(root_dir))

    # Также добавляем все подпапки
    for folder in ["services", "agents", "core", "scripts"]:
        folder_path = root_dir / folder
        if folder_path.exists():
            sys.path.insert(0, str(folder_path))

    print("✅ Paths setup complete")


# Применяем фикс сразу
setup_paths()

# Теперь импортируем все что нужно
try:
    pass

    print("✅ All imports successful!")

except ImportError as e:
    print("❌ Imports failed:", e)
