import json
import re
from pathlib import Path
from typing import Dict, Any


class DataHarvester:
    """
    Сервис для извлечения данных из docs/ и конвертации их в параметры для Registry.
    """

    def __init__(self, root_dir: Path):
        self.docs_dir = root_dir / "docs"
        self.registry_path = root_dir / "database" / "registry.json"

    def harvest_materials(self):
        """Проходит по всем .txt и .md в docs/materials и ищет параметры."""
        mat_path = self.docs_dir / "materials"
        if not mat_path.exists():
            mat_path.mkdir(parents=True)
            return "Папка docs/materials была пуста. Создана структура."

        new_materials = 0
        for file in mat_path.glob("*.txt"):
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                # Извлекаем данные с помощью регулярных выражений или LLM
                data = self._parse_material_text(content)
                if data:
                    self._update_registry("materials", data)
                    new_materials += 1

        return f"Успешно обработано материалов: {new_materials}"

    def _parse_material_text(self, text: str) -> Dict[str, Any]:
        """
        Логика парсинга: ищем ключевые слова в историческом тексте.
        Например: 'Плотность: 7800 кг/м3', 'Тип: Сталь'
        """
        # Ищем ID или имя
        name_match = re.search(r"Название:\s*(.*)", text)
        density_match = re.search(r"Плотность:\s*(\d+)", text)

        if not name_match:
            return None

        name = name_match.group(1).strip()
        uid = f"MAT_{name.upper().replace(' ', '_')}"

        return {
            "uid": uid,
            "internal_name": name,
            "physics": {
                "density": int(density_match.group(1)) if density_match else 7800,
                "durability": 100,
            },
            "visual": {
                "roughness": 0.5,  # Дефолт, который потом поправит ИИ
                "metallic": 1.0,
            },
        }

    def _update_registry(self, category: str, data: Dict[str, Any]):
        with open(self.registry_path, "r+", encoding="utf-8") as f:
            registry = json.load(f)
            registry[category][data["uid"]] = data
            f.seek(0)
            json.dump(registry, f, indent=4, ensure_ascii=False)
            f.truncate()
