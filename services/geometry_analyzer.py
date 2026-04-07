"""
Семантический анализ геометрии
Превращает "стол" в структурированное описание компонентов
"""

from typing import Dict, Any
from loguru import logger


class GeometryAnalyzer:
    """Анализатор, который понимает структуру объектов"""

    def __init__(self, llm_service):
        self.llm = llm_service

    async def analyze(self, object_name: str, context: str = "") -> Dict[str, Any]:
        """
        Анализ объекта и возврат его геометрической структуры

        Args:
            object_name: название объекта (стол, клинок, дерево, стул)
            context: дополнительный контекст (размеры, стиль)

        Returns:
            {
                "object_type": "table",
                "components": [...],
                "materials": {...},
                "modifiers": [...]
            }
        """
        prompt = self._build_analysis_prompt(object_name, context)
        response = await self.llm.generate_json(prompt)
        logger.info(
            f"📐 Analyzed {object_name}: {len(response.get('components', []))} components"
        )
        return response

    def _build_analysis_prompt(self, object_name: str, context: str) -> str:
        return f"""
        Ты эксперт по 3D-геометрии. Проанализируй объект "{object_name}" и опиши его геометрическую структуру.

Контекст: {context if context else "стандартный"}

КЛЮЧЕВЫЕ ПРАВИЛА:
1. Меч = лезвие + гарда + рукоять + навершие
2. Стол = столешница + ножки (4 шт)
3. Дерево = ствол + ветви + крона
4. Стул = сиденье + спинка + ножки

Если объект "sword" или "меч", ВСЕГДА используй структуру меча, НЕ generic.

Верни ТОЛЬКО JSON в формате:
{{
    "object_type": "sword",
    "components": [
        {{"name": "blade", "type": "extruded_shape", "points": [[0,0], [0.08,0.4], [0.05,0.8], [0,1.2], [-0.05,0.8], [-0.08,0.4]], "height": 2.0, "position": [0, 0, 0]}},
        {{"name": "guard", "type": "box", "width": 0.3, "height": 0.08, "depth": 0.15, "position": [0, 0, 1.0]}},
        {{"name": "handle", "type": "cylinder", "radius": 0.08, "height": 0.7, "position": [0, 0, 1.4]}},
        {{"name": "pommel", "type": "sphere", "radius": 0.1, "position": [0, 0, 1.8]}}
    ],
    "materials": {{
        "blade": "metal",
        "guard": "metal",
        "handle": "wood",
        "pommel": "metal"
    }},
    "modifiers": ["bevel"]
}}
Ты эксперт по 3D-геометрии. Проанализируй объект "{object_name}" и опиши его геометрическую структуру.

Контекст: {context if context else "стандартный"}

ПРАВИЛА ДЛЯ РАЗНЫХ ТИПОВ ОБЪЕКТОВ:

1. СТОЛ = столешница + ножки (4 шт) + царги (опционально)
   - Столешница: box, ширина 2.0, высота 0.1, глубина 1.5
   - Ножки: box, ширина 0.1, высота 1.0, глубина 0.1

2. КЛИНОК/МЕЧ = лезвие + гарда + рукоять + навершие
   - Лезвие: extruded_shape (ромбовидное сечение), высота 2.0
   - Гарда: box или torus, ширина 0.3
   - Рукоять: cylinder, радиус 0.08, высота 0.8
   - Навершие: sphere, радиус 0.1

3. ДЕРЕВО = ствол + ветви (3-5 шт) + крона
   - Ствол: cylinder, радиус 0.3, высота 2.0
   - Ветви: cylinder с ротацией
   - Крона: sphere или cone, радиус 0.8

4. СТУЛ = сиденье + спинка + ножки (4 шт)
   - Сиденье: box, ширина 0.5, высота 0.1, глубина 0.5
   - Спинка: box, ширина 0.5, высота 0.5, глубина 0.05
   - Ножки: box, высота 0.5

5. ДОМ = стены + крыша + дверь + окна
   - Стены: box, ширина 3.0, высота 2.0, глубина 3.0
   - Крыша: cone, радиус 2.0, высота 1.5

6. ПЕРСОНАЖ = тело + голова + руки + ноги
   - Тело: cylinder или box
   - Голова: sphere
   - Руки: cylinder
   - Ноги: cylinder

7. МАШИНА = кузов + колеса (4 шт) + окна
   - Кузов: box с закруглениями
   - Колеса: cylinder или torus

Верни JSON в точном формате:
{{
    "object_type": "тип_объекта",
    "components": [
        {{
            "name": "название_компонента",
            "type": "box|cylinder|sphere|cone|extruded_shape|torus",
            "width": число,
            "height": число,
            "depth": число,
            "radius": число,
            "radius2": число (для torus),
            "points": [[x,y], [x,y], ...] (для extruded_shape),
            "position": [x, y, z],
            "rotation": [rx, ry, rz],
            "parent": "имя_родителя"
        }}
    ],
    "connections": [
        {{"from": "компонент1", "to": "компонент2", "type": "attach"}}
    ],
    "materials": {{
        "компонент": "wood|metal|plastic|glass|red|blue|green",
        "default": "wood"
    }},
    "modifiers": ["bevel", "subdivision", "array"]
}}

Пример для стола:
{{
    "object_type": "table",
    "components": [
        {{"name": "top", "type": "box", "width": 2.0, "height": 0.1, "depth": 1.5, "position": [0, 0, 1.0]}},
        {{"name": "leg1", "type": "box", "width": 0.1, "height": 1.0, "depth": 0.1, "position": [-0.9, -0.7, 0.5]}},
        {{"name": "leg2", "type": "box", "width": 0.1, "height": 1.0, "depth": 0.1, "position": [0.9, -0.7, 0.5]}},
        {{"name": "leg3", "type": "box", "width": 0.1, "height": 1.0, "depth": 0.1, "position": [-0.9, 0.7, 0.5]}},
        {{"name": "leg4", "type": "box", "width": 0.1, "height": 1.0, "depth": 0.1, "position": [0.9, 0.7, 0.5]}}
    ],
    "materials": {{"default": "wood"}},
    "modifiers": ["bevel"]
}}

Пример для клинка:
{{
    "object_type": "sword",
    "components": [
        {{"name": "blade", "type": "extruded_shape", "points": [[0,0], [0.08,0.3], [0.05,0.6], [0,1], [-0.05,0.6], [-0.08,0.3]], "height": 2.0, "position": [0, 0, 0]}},
        {{"name": "guard", "type": "box", "width": 0.3, "height": 0.05, "depth": 0.2, "position": [0, 0, 1.0]}},
        {{"name": "handle", "type": "cylinder", "radius": 0.08, "height": 0.8, "position": [0, 0, 1.4]}},
        {{"name": "pommel", "type": "sphere", "radius": 0.1, "position": [0, 0, 1.9]}}
    ],
    "materials": {{
        "blade": "metal",
        "guard": "metal",
        "handle": "wood",
        "pommel": "metal"
    }},
    "modifiers": ["bevel", "subdivision"]
}}

Верни ТОЛЬКО JSON, без пояснений.
"""
