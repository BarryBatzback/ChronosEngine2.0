# scripts/check_docs_structure.py
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

DOCS_PATH = r"D:\ChronosEngine2.0\tools\blender_python_reference_5_1"

print(f"Checking: {DOCS_PATH}")

# Проверим структуру папки
path = Path(DOCS_PATH)
if not path.exists():
    print("❌ Path doesn't exist!")
    exit()

print("\n📁 Directory structure:")
for item in path.iterdir():
    if item.is_dir():
        print(f"📂 {item.name}/")
        # Посмотрим что внутри первых 5 подпапок
        subitems = list(item.iterdir())[:3]
        for subitem in subitems:
            print(f"    └── {subitem.name} ({'dir' if subitem.is_dir() else 'file'})")
    else:
        print(f"📄 {item.name}")

# Посчитаем HTML файлы
html_files = list(path.rglob("*.html"))
print(f"\n📊 Total HTML files: {len(html_files)}")

if html_files:
    print("\nFirst 5 HTML files:")
    for f in html_files[:5]:
        print(f"  - {f.relative_to(path)}")
