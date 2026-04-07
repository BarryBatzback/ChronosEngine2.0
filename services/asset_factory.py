import uuid
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any


class AssetFactory:
    """
    Сервис управления реестром ассетов и генерации уникальных метаданных.
    Отвечает за целостность базы данных registry.json и именование.
    """

    def __init__(self, root_path: Path):
        self.root = Path(root_path)
        self.registry_path = self.root / "data" / "registry.json"
        self._ensure_registry_exists()

    def generate_uid(self, prefix: str = "MSH") -> str:
        """
        Генерирует стандартизированный UID для Chronos Engine.
        Формат: [PREFIX]_[HASH]_[TIMESTAMP]
        """
        short_hash = str(uuid.uuid4()).split("-")[0].upper()
        timestamp = int(time.time())
        return f"{prefix}_{short_hash}_{timestamp}"

    def get_asset_data(self, asset_id: str) -> Dict[str, Any]:
        """Безопасное получение данных ассета из реестра."""
        registry = self._load_registry()
        return registry.get(asset_id, {})

    def register_asset(self, asset_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Регистрирует новый ассет в системе.
        Централизованный метод записи, исключающий дублирование в Orchestrator.
        """
        try:
            registry = self._load_registry()

            registry[asset_id] = {
                "timestamp": time.ctime(),
                "unix_time": int(time.time()),
                **metadata,
            }

            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=4, ensure_ascii=False)

            logging.info(f"💾 Asset {asset_id} registered in database.")
            return True
        except Exception as e:
            logging.error(f"❌ Failed to register asset: {e}")
            return False

    def _load_registry(self) -> Dict[str, Any]:
        """Внутренний метод загрузки данных."""
        if not self.registry_path.exists():
            return {}
        try:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.warning("⚠️ Registry file corrupted, starting fresh.")
            return {}

    def _ensure_registry_exists(self):
        """Гарантирует наличие структуры папок для БД."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.registry_path.exists():
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump({}, f)
