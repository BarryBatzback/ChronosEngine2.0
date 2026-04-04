
import re
from typing import Dict, Any
from loguru import logger


class CodeAgent:
    def __init__(self, llm_service):
        self.llm = llm_service

    async def generate_code(self, plan: Dict[str, Any]) -> str:
        prompt = f"Создай код для Blender: {plan}"
        raw_code = await self.llm.generate(prompt)
        return self._clean_code(raw_code)

    def _clean_code(self, code: str) -> str:
        code = re.sub(r'```python\s*', '', code)
        code = re.sub(r'```\s*', '', code)
        return code.strip()

    async def fix_code(self, code: str, error: str) -> str:
        prompt = f"Исправь код: {code}\nОшибка: {error}"
        fixed = await self.llm.generate(prompt)
        return self._clean_code(fixed)