import re
import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional


class ArchitectureParser:
    """
    Сервис для парсинга текстовых описаний строений и материалов
    и их конвертации в структурированную базу данных JSON для Chronos Engine.
    """

    def __init__(self, root_dir: Optional[Path] = None):
        # Если путь не передан, определяем корень проекта относительно файла
        self.root = root_dir or Path(__file__).resolve().parent.parent
        self.docs_dir = self.root / "docs"
        self.registry_path = self.root / "database" / "registry.json"

        # Шаблон пустой базы данных, если файла еще нет
        self.default_registry = {
            "metadata": {"version": "2.0", "game_setting": "Eurasia 800-900 AD"},
            "materials": {},
            "meshes": {},
        }

    def _ensure_directories(self):
        """Гарантирует существование необходимых папок и файлов."""
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.registry_path.exists():
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump(self.default_registry, f, indent=4, ensure_ascii=False)

    def load_registry(self) -> Dict[str, Any]:
        """Загружает текущую базу данных."""
        self._ensure_directories()
        with open(self.registry_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_registry(self, data: Dict[str, Any]):
        """Сохраняет обновленную базу данных."""
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def parse_text_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Читает текстовый файл и извлекает из него параметры на основе тегов
        и ключевых слов.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Ошибка при чтении файла {file_path}: {e}")
            return None

        # Регулярные выражения для поиска основных тегов
        category_match = re.search(r"\[CATEGORY:\s*(.*?)\]", content)
        sub_type_match = re.search(r"\[SUB_TYPE:\s*(.*?)\]", content)
        id_match = re.search(r"\[ID:\s*(.*?)\]", content)

        if not category_match:
            print(f"Пропуск файла {file_path.name}: не найден тег CATEGORY")
            return None

        category = category_match.group(1).strip().lower()
        sub_type = (
            sub_type_match.group(1).strip().lower() if sub_type_match else "general"
        )
        custom_id = id_match.group(1).strip() if id_match else None

        # Создаем уникальный UID, если он не задан в файле
        uid = custom_id or f"MSH_{category[:3].upper()}_{uuid.uuid4().hex[:6].upper()}"

        # Извлечение описания
        desc_match = re.search(
            r"ОПИСАНИЕ:\s*(.*?)(?=\n\[|\nПАРАМЕТРЫ|$)", content, re.DOTALL
        )
        description = desc_match.group(1).strip() if desc_match else ""

        # Извлечение параметров (ключ: значение)
        params = {}
        param_section = re.search(
            r"ПАРАМЕТРЫ ДЛЯ GENERATOR:(.*?)(?=\n\[|\n\n|$)", content, re.DOTALL
        )
        if param_section:
            param_lines = param_section.group(1).strip().split("\n")
            for line in param_lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().replace("-", "").replace("*", "")
                    # Пытаемся распарсить числа и размерности
                    val_str = value.strip()
                    if "m" in val_str and any(char.isdigit() for char in val_str):
                        # Извлекаем метры как float
                        val_num = re.findall(r"[-+]?\d*\.\d+|\d+", val_str)
                        params[key] = float(val_num[0]) if val_num else val_str
                    else:
                        params[key] = val_str

        # Извлечение габаритов для 3D художников и генераторов
        dimensions = {}
        dim_match = re.search(r"Размеры:\s*(.*)", content)
        if dim_match:
            dim_str = dim_match.group(1)
            # Ищем все числа (длина, ширина, высота)
            nums = re.findall(r"[-+]?\d*\.\d+|\d+", dim_str)
            if len(nums) >= 3:
                dimensions = {
                    "length": float(nums[0]),
                    "width": float(nums[1]),
                    "height": float(nums[2]),
                }

        # Формируем итоговую структуру под геймдизайнерские нужды
        return {
            "uid": uid,
            "category": category,
            "sub_category": sub_type,
            "description": description,
            "visual_data": {"dimensions": dimensions, "generation_params": params},
            "status": "raw_description",
        }

    def process_docs_folder(self):
        """Сканирует всю папку docs и наполняет registry.json."""
        registry = self.load_registry()
        processed_count = 0

        # Ищем все файлы .txt во всех подпапках docs/
        for file_path in self.docs_dir.rglob("*.txt"):
            parsed_data = self.parse_text_file(file_path)

            if parsed_data:
                uid = parsed_data["uid"]
                # Записываем в секцию meshes
                registry["meshes"][uid] = parsed_data
                processed_count += 1
                print(f"Загружен ассет: {uid} ({parsed_data['category']})")

        self.save_registry(registry)
        return (
            f"Парсинг завершен. Всего обработано и добавлено ассетов: {processed_count}"
        )


# Пример использования
if __name__ == "__main__":
    # Предполагается запуск из корня проекта: python services/architecture_parser.py
    parser = ArchitectureParser()
    result = parser.process_docs_folder()
    print(result)
