from typing import Dict, List
from loguru import logger


class SemanticAnalyzer:
    def __init__(self, llm_service=None):
        """
        Инициализация.
        llm_service теперь опционален, чтобы не возникало TypeError: __init__() takes 1 positional argument but 2 were given
        """
        self.llm = llm_service

        # База знаний объектов (Hardcoded Rules)
        self.object_rules = {
            "sword": {
                "keywords": [
                    "sword",
                    "blade",
                    "weapon",
                    "katana",
                    "rapier",
                    "claymore",
                ],
                "components": [
                    {
                        "name": "blade",
                        "type": "extruded",
                        "dimensions": [0.1, 0.02, 1.2],
                        "material": "metal",
                    },
                    {
                        "name": "guard",
                        "type": "box",
                        "dimensions": [0.25, 0.06, 0.04],
                        "material": "metal",
                    },
                    {
                        "name": "handle",
                        "type": "cylinder",
                        "dimensions": [0.04, 0.04, 0.4],
                        "material": "wood",
                    },
                    {
                        "name": "pommel",
                        "type": "sphere",
                        "dimensions": [0.06, 0.06, 0.06],
                        "material": "metal",
                    },
                ],
            },
            "table": {
                "keywords": ["table", "desk", "furniture"],
                "components": [
                    {
                        "name": "top",
                        "type": "box",
                        "dimensions": [1.2, 0.05, 0.8],
                        "material": "wood",
                    },
                    {
                        "name": "leg1",
                        "type": "cylinder",
                        "dimensions": [0.05, 0.05, 0.9],
                        "material": "wood",
                    },
                    {
                        "name": "leg2",
                        "type": "cylinder",
                        "dimensions": [0.05, 0.05, 0.9],
                        "material": "wood",
                    },
                    {
                        "name": "leg3",
                        "type": "cylinder",
                        "dimensions": [0.05, 0.05, 0.9],
                        "material": "wood",
                    },
                    {
                        "name": "leg4",
                        "type": "cylinder",
                        "dimensions": [0.05, 0.05, 0.9],
                        "material": "wood",
                    },
                ],
            },
            "tree": {
                "keywords": ["tree", "plant", "forest", "oak", "pine"],
                "components": [
                    {
                        "name": "trunk",
                        "type": "cylinder",
                        "dimensions": [0.2, 0.2, 2.0],
                        "material": "wood",
                    },
                    {
                        "name": "foliage",
                        "type": "sphere",
                        "dimensions": [1.0, 1.0, 1.0],
                        "material": "leaves",
                    },
                ],
            },
        }

        self.materials = {
            "metal": {"color": [0.8, 0.8, 0.9], "roughness": 0.2},
            "gold": {"color": [0.9, 0.8, 0.2], "roughness": 0.3},
            "wood": {"color": [0.3, 0.2, 0.1], "roughness": 0.8},
            "leaves": {"color": [0.1, 0.5, 0.1], "roughness": 0.9},
            "default": {"color": [0.8, 0.8, 0.8], "roughness": 0.5},
        }

    async def analyze(self, user_prompt: str, api_context: str = "") -> Dict:
        """
        Основной метод анализа. Оставлен async для совместимости с интерфейсом GeometryAgent.
        """
        logger.info(f"🔍 Rule-based analysis: {user_prompt}")

        # Если объект сложный и у нас есть LLM, можно делегировать ей (опционально)
        # Но сейчас используем вашу логику правил:
        return self._analyze_sync(user_prompt)

    def _analyze_sync(self, prompt: str) -> Dict:
        prompt_lower = prompt.lower()
        object_type = self._detect_object_type(prompt_lower)
        components = self._get_components(object_type, prompt_lower)
        materials = self._adjust_materials(object_type, prompt_lower)

        return {
            "object_type": object_type,
            "components": components,
            "materials": materials,
        }

    def _detect_object_type(self, prompt: str) -> str:
        for obj_type, rules in self.object_rules.items():
            if any(keyword in prompt for keyword in rules["keywords"]):
                return obj_type
        return "object"

    def _get_components(self, object_type: str, prompt: str) -> List[Dict]:
        if object_type in self.object_rules:
            # Важно: используем глубокое копирование, чтобы не менять оригинальные правила
            import copy

            components = copy.deepcopy(self.object_rules[object_type]["components"])

            # Модификаторы размера
            if any(word in prompt for word in ["large", "big", "huge", "great"]):
                for comp in components:
                    comp["dimensions"] = [d * 1.8 for d in comp["dimensions"]]
            elif any(word in prompt for word in ["small", "tiny", "short"]):
                for comp in components:
                    comp["dimensions"] = [d * 0.6 for d in comp["dimensions"]]

            return components

        return [
            {
                "name": "main",
                "type": "cube",
                "dimensions": [1, 1, 1],
                "material": "default",
            }
        ]

    def _adjust_materials(self, object_type: str, prompt: str) -> Dict:
        materials = {}
        # Загрузка базовых материалов
        if object_type == "sword":
            materials = {
                "metal": self.materials["metal"].copy(),
                "wood": self.materials["wood"].copy(),
            }
        elif object_type == "tree":
            materials = {
                "wood": self.materials["wood"].copy(),
                "leaves": self.materials["leaves"].copy(),
            }
        else:
            materials = {"default": self.materials["default"].copy()}

        # Цветовые модификации
        if "gold" in prompt:
            if "metal" in materials:
                materials["metal"] = self.materials["gold"].copy()
        if "red" in prompt:
            for mat in materials.values():
                mat["color"] = [0.8, 0.0, 0.0]
        if "black" in prompt:
            for mat in materials.values():
                mat["color"] = [0.02, 0.02, 0.02]

        return materials
