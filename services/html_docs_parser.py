# services/html_docs_parser.py
from pathlib import Path
from bs4 import BeautifulSoup
import re
from typing import List, Dict
from loguru import logger


class HTMLDocsParser:
    def __init__(self, docs_path: str):
        self.docs_path = Path(docs_path)

    def parse_all(self) -> List[Dict]:
        """Парсит HTML файлы документации Blender с оптимизацией"""
        docs = []

        # Ищем все HTML файлы
        html_files = list(self.docs_path.rglob("*.html"))
        logger.info(f"Found {len(html_files)} HTML files to process")

        # Обрабатываем файлы партиями по 100
        for i, html_file in enumerate(html_files):
            if i % 100 == 0:
                logger.info(f"Processing file {i}/{len(html_files)}")

            try:
                doc = self._parse_blender_api_file(html_file)
                if doc:
                    docs.append(doc)

            except Exception as e:
                logger.warning(f"Failed to parse {html_file}: {e}")
                continue

        return docs

    def _parse_blender_api_file(self, html_file: Path) -> Dict:
        """Специализированный парсер для файлов Blender API"""
        with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

            # Извлекаем заголовок и тип API
            title = soup.find("title")
            title_text = title.get_text() if title else html_file.stem

            # Определяем тип API элемента
            api_type = self._detect_api_type(title_text, html_file.name)

            # Извлекаем основной контент
            main_content = (
                soup.find("div", {"role": "main"})
                or soup.find("div", {"class": "body"})
                or soup.body
            )
            text = (
                main_content.get_text(separator="\n", strip=True)
                if main_content
                else ""
            )

            # Очищаем и структурируем текст
            text = self._clean_api_text(text)

            # Извлекаем сигнатуру функции/класса
            signature = self._extract_signature(soup)

            return {
                "type": api_type,
                "name": title_text,
                "signature": signature,
                "content": text[:2500],  # Ограничиваем для эффективности
                "source_file": str(html_file.relative_to(self.docs_path)),
            }

    def _detect_api_type(self, title: str, filename: str) -> str:
        """Определяет тип API элемента"""
        if "bpy.types." in filename:
            return "class"
        elif "bpy.ops." in filename:
            return "operator"
        elif "bpy.data." in filename:
            return "data"
        elif "bpy.context." in filename:
            return "context"
        elif any(ext in filename for ext in ["bmesh", "mathutils", "gpu"]):
            return "module"
        else:
            return "general"

    def _clean_api_text(self, text: str) -> str:
        """Очищает текст API документации"""
        # Удаляем повторяющиеся новые строки
        text = re.sub(r"\n\s*\n", "\n\n", text)
        # Удаляем лишние пробелы
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def _extract_signature(self, soup: BeautifulSoup) -> str:
        """Извлекает сигнатуру функции/класса"""
        # Ищем блоки с кодом
        code_blocks = soup.find_all("code", {"class": "code"})
        for code in code_blocks:
            text = code.get_text().strip()
            if text.startswith(("def ", "class ")):
                return text
        return ""
