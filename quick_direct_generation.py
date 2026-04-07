# quick_direct_generation.py
from agents.geometry_agent import GeometryAgent

# Сохраняем оригинальный метод
original_execute = GeometryAgent.execute


async def direct_execute(self, task: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    user_prompt = task.get("prompt", task.get("object_name", "generic"))
    logger.info(f"🎨 Direct generation: {user_prompt}")

    try:
        # 🔥 ПРОПУСКАЕМ МЕДЛЕННЫЙ LLM АНАЛИЗ!
        # Используем прямое преобразование запроса в структуру
        structure = self._prompt_to_structure(user_prompt)

        logger.info(
            f"📐 Direct structure: {structure.get('object_type')} with {len(structure.get('components', []))} components"
        )

        # 🔥 Генерируем код напрямую без API контекста (для скорости)
        code = self.generator.generate_code(structure, "")
        logger.info(f"📝 Generated {len(code)} chars of code")

        # Выполнение в Blender
        result = await self.blender.run_python(code)

        if result.get("status") == "ok":
            return {
                "success": True,
                "message": f"Created {structure.get('object_type')}",
                "code": code,
                "structure": structure,
            }
        else:
            return await self._fix_and_retry(
                code, result.get("message", ""), structure, user_prompt
            )

    except Exception as e:
        logger.error(f"❌ Direct generation failed: {e}")
        return {"success": False, "message": str(e), "code": ""}


def _prompt_to_structure(self, prompt: str) -> Dict:
    """Прямое преобразование запроса в структуру (быстрое)"""
    prompt_lower = prompt.lower()

    if any(word in prompt_lower for word in ["sword", "blade", "weapon"]):
        return {
            "object_type": "sword",
            "components": [
                {
                    "name": "blade",
                    "type": "extruded",
                    "dimensions": [0.1, 0.02, 1.2],
                    "position": [0, 0, 0.6],
                    "material": "metal",
                },
                {
                    "name": "guard",
                    "type": "box",
                    "dimensions": [0.25, 0.06, 0.04],
                    "position": [0, 0, 0.1],
                    "material": "gold",
                },
                {
                    "name": "handle",
                    "type": "cylinder",
                    "dimensions": [0.04, 0.04, 0.4],
                    "position": [0, 0, -0.3],
                    "material": "wood",
                },
                {
                    "name": "pommel",
                    "type": "sphere",
                    "dimensions": [0.06, 0.06, 0.06],
                    "position": [0, 0, -0.5],
                    "material": "gold",
                },
            ],
            "materials": {
                "metal": {"color": [0.8, 0.8, 0.9], "roughness": 0.2},
                "gold": {"color": [0.9, 0.8, 0.2], "roughness": 0.3},
                "wood": {"color": [0.3, 0.2, 0.1], "roughness": 0.8},
            },
        }
    else:
        # Fallback для других объектов
        return {
            "object_type": "object",
            "components": [
                {
                    "name": "main",
                    "type": "cube",
                    "dimensions": [1, 1, 1],
                    "position": [0, 0, 0],
                    "material": "default",
                }
            ],
        }


# Применяем monkey patch
GeometryAgent.execute = direct_execute
GeometryAgent._prompt_to_structure = _prompt_to_structure

print("✅ Direct generation mode activated - FAST! ⚡")
