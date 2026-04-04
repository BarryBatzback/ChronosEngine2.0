"""
Агент-координатор для анализа запросов
"""

import json
from typing import Dict, Any, List
from loguru import logger


class CoordinatorAgent:
    """Агент для анализа запросов и создания планов"""

    def __init__(self, llm_service):
        self.llm = llm_service

    async def analyze(self, user_request: str) -> Dict[str, Any]:
        """Анализ запроса и создание плана"""
        prompt = f"""
Проанализируй запрос: "{user_request}"

Определи тип объекта и верни JSON в формате:
{{
    "object_type": "тип_объекта",
    "components": [],
    "materials": [],
    "dimensions": {{}},
    "special_features": []
}}

Варианты object_type: table, sword, tree, chair, house, character, generic

Верни ТОЛЬКО JSON, без пояснений.
"""
        response = await self.llm.generate_json(prompt)
        return response

    async def decompose(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Декомпозиция плана на задачи"""
        tasks = [
            {
                "type": "geometry",
                "plan": plan,
                "description": f"Create {plan.get('object_type', 'object')}"
            }
        ]
        
        # Добавляем задачу на материалы
        materials = plan.get('materials', [])
        for material in materials:
            tasks.append({
                "type": "material",
                "material_type": material,
                "description": f"Apply {material} material"
            })
        
        return tasks