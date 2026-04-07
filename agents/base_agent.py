"""
Базовый класс для всех агентов
"""

from abc import ABC, abstractmethod
from typing import Dict
from datetime import datetime
from loguru import logger


class BaseAgent(ABC):
    """Базовый класс агента"""

    def __init__(self, name: str, llm_service):
        self.name = name
        self.llm = llm_service
        self.created_at = datetime.now()

    @abstractmethod
    async def execute(self, task: Dict, session_id: str) -> "TaskResult":
        """Выполнение задачи"""

    async def validate_input(self, task: Dict) -> bool:
        """Валидация входных данных"""
        required_fields = task.get("required_fields", [])
        for field in required_fields:
            if field not in task:
                logger.error(f"Missing required field: {field}")
                return False
        return True

    def log_action(self, session_id: str, action: str, details: Dict):
        """Логирование действия"""
        logger.info(f"[{self.name}] {action}: {details}")
