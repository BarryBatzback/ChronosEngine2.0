# quick_json_fix.py
import json
import re


def fix_json_response(text: str) -> str:
    """Быстрое исправление JSON ответов от LLM"""
    # Удаляем всё до первой { и после последней }
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        return '{"object_type": "object", "components": []}'

    json_str = text[start : end + 1]

    # Исправляем распространенные ошибки
    json_str = re.sub(r",\s*}", "}", json_str)
    json_str = re.sub(r",\s*]", "]", json_str)
    json_str = re.sub(r"'", '"', json_str)  # Заменяем одинарные кавычки

    try:
        # Пробуем распарсить чтобы проверить
        json.loads(json_str)
        return json_str
    except:
        # Если всё равно не работает, возвращаем fallback
        return '{"object_type": "object", "components": []}'


# Монkey patch для LLMService
from services.llm_service import LLMService

original_clean = LLMService._clean_json_response


def fixed_clean_json_response(self, text: str) -> str:
    result = original_clean(self, text)
    return fix_json_response(result)


LLMService._clean_json_response = fixed_clean_json_response

print("✅ JSON fix applied")
