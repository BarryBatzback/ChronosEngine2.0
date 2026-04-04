# scripts/index_blender_docs.py
"""
Скрипт для индексации HTML документации Blender
"""

import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.blender_knowledge_base import BlenderKnowledgeBase
from loguru import logger


def main():
    # Путь к папке с HTML документацией
    docs_path = "D:/blender_docs/html"  # Укажите ваш путь
    
    logger.info(f"📚 Indexing documentation from: {docs_path}")
    
    kb = BlenderKnowledgeBase(docs_path=docs_path)
    
    logger.info("✅ Indexing complete!")


if __name__ == "__main__":
    main()