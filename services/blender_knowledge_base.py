"""
База знаний по Blender API с использованием векторного поиска
"""

import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger

# Для эмбеддингов (локально, бесплатно)
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions


class BlenderKnowledgeBase:
    """
    Векторная база знаний по Blender API
    Позволяет искать релевантные фрагменты документации
    """

    def __init__(self, docs_path: str = None, persist_dir: str = "./chroma_db"):
        self.persist_dir = Path(persist_dir)
        self.collection_name = "blender_api"

        # Инициализируем эмбеддер (локальный)
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

        # Инициализируем ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))

        # Создаём или получаем коллекцию
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            ),
        )

        # Загружаем документацию если коллекция пуста
        if docs_path and self.collection.count() == 0:
            self._index_documentation(docs_path)

    def _index_documentation(self, docs_path: str):
        """Индексация HTML документации"""
        from services.html_docs_parser import HTMLDocsParser

        parser = HTMLDocsParser(docs_path)
        docs = parser.parse_all()

        for i, doc in enumerate(docs):
            # Создаём текст для индексации
            text = f"""
Type: {doc['type']}
Name: {doc['name']}
Signature: {doc.get('signature', '')}
Description: {doc.get('description', '')}
            """.strip()

            # Добавляем в коллекцию
            self.collection.add(
                ids=[f"doc_{hashlib.md5(doc['name'].encode()).hexdigest()[:16]}"],
                documents=[text],
                metadatas=[
                    {
                        "name": doc["name"],
                        "type": doc["type"],
                        "signature": doc.get("signature", "")[:200],
                        "source": doc.get("source_file", ""),
                    }
                ],
            )

        logger.info(f"📚 Indexed {len(docs)} documentation entries")

    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Поиск релевантных фрагментов документации

        Args:
            query: Поисковый запрос
            n_results: Количество результатов

        Returns:
            Список найденных фрагментов
        """
        results = self.collection.query(query_texts=[query], n_results=n_results)

        docs = []
        if results["documents"] and results["documents"][0]:
            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                docs.append(
                    {
                        "content": doc,
                        "name": meta.get("name", ""),
                        "type": meta.get("type", ""),
                        "signature": meta.get("signature", ""),
                        "relevance": 1.0,
                    }
                )

        return docs

    def get_api_signature(self, name: str) -> Optional[str]:
        """Получение сигнатуры API по имени"""
        results = self.collection.query(query_texts=[name], n_results=1)

        if results["metadatas"] and results["metadatas"][0]:
            return results["metadatas"][0][0].get("signature", "")
        return None

    def get_context_for_llm(self, query: str, max_results: int = 3) -> str:
        """
        Получение контекста для LLM на основе запроса

        Args:
            query: Запрос пользователя
            max_results: Максимум релевантных фрагментов

        Returns:
            Строка с контекстом для промпта
        """
        results = self.search(query, max_results)

        if not results:
            return ""

        context = "# Blender API Documentation (relevant snippets)\n\n"

        for r in results:
            context += f"## {r['name']} ({r['type']})\n"
            if r["signature"]:
                context += f"**Signature:** `{r['signature']}`\n\n"
            context += f"{r['content'][:500]}\n\n"
            context += "---\n\n"

        return context
