# scripts/init_knowledge_base.py
import sys
import os
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from services.blender_knowledge_base import BlenderKnowledgeBase
from loguru import logger

if __name__ == "__main__":
    # Правильный путь к документации
    DOCS_PATH = r"D:\ChronosEngine2.0\tools\blender_python_reference_5_1"
    
    logger.info(f"📁 Using documentation path: {DOCS_PATH}")
    
    # Проверяем существует ли путь
    if not os.path.exists(DOCS_PATH):
        logger.error(f"❌ Path does not exist: {DOCS_PATH}")
        exit(1)
    
    # Проверяем есть ли HTML файлы
    html_files = list(Path(DOCS_PATH).rglob("*.html"))
    logger.info(f"📄 Found {len(html_files)} HTML files")
    
    if not html_files:
        logger.warning("No HTML files found. Check your documentation path.")
        # Посмотрим что есть в папке
        items = list(Path(DOCS_PATH).iterdir())
        print("Contents of directory:")
        for item in items[:10]:  # первые 10 элементов
            print(f"  - {item.name} ({'dir' if item.is_dir() else 'file'})")
        exit(1)
    
    # Инициализируем базу знаний
    logger.info("Initializing knowledge base...")
    kb = BlenderKnowledgeBase(docs_path=DOCS_PATH)
    
    # Проверяем что добавилось
    count = kb.collection.count()
    logger.success(f"✅ Knowledge base initialized with {count} documents!")
