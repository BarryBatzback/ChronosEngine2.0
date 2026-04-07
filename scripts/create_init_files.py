# scripts/create_init_files.py
from pathlib import Path


def create_init_files():
    """Создает __init__.py файлы во всех папках"""
    folders = [
        Path("services"),
        Path("agents"),
        Path("core"),
        Path("scripts"),
        Path("blender_addon"),
        Path("config"),
        Path("database"),
        Path("docs"),
        Path("logs"),
        Path("output"),
        Path("tests"),
        Path("tools"),
        Path("web_ui"),
        Path("workflows"),
    ]

    for folder in folders:
        if folder.exists():
            init_file = folder / "__init__.py"
            if not init_file.exists():
                init_file.write_text("# Package initialization\n")
                print(f"✅ Created: {init_file}")
            else:
                print(f"📁 Already exists: {init_file}")
        else:
            print(f"❌ Folder doesn't exist: {folder}")


if __name__ == "__main__":
    create_init_files()
