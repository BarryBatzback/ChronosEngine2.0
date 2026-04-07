import json
import asyncio
import logging
from pathlib import Path
from core.orchestrator import Orchestrator

# Настройка логирования для наглядности в консоли
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%H:%M:%S",
)


async def test_palisade_generation():
    root_dir = Path(__file__).resolve().parent
    registry_path = root_dir / "database" / "registry.json"

    logging.info("🔍 Шаг 1: Чтение базы данных registry.json...")

    if not registry_path.exists():
        logging.error(
            "❌ Файл базы данных не найден! Сначала запусти services/architecture_parser.py"
        )
        return

    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    # Ищем наш частокол
    asset_uid = "STR_PALISADE_MOD_01"
    asset_data = registry.get("meshes", {}).get(asset_uid)

    if not asset_data:
        logging.error(f"❌ Ассет {asset_uid} не найден в базе данных!")
        return

    logging.info(f"✅ Данные для {asset_uid} успешно извлечены.")

    # Извлекаем параметры для промпта
    v_data = asset_data.get("visual_data", {})
    dims = v_data.get("dimensions", {})
    params = v_data.get("generation_params", {})

    # Шаг 2: Формирование идеального технического промпта на основе параметров
    prompt = f"""
Напиши Python скрипт для Blender (используя ТОЛЬКО bmesh), который генерирует модульный частокол.
Название результирующего меша должно быть: "{asset_uid}".

ФИЗИЧЕСКИЕ РАЗМЕРЫ МОДУЛЯ:
- Длина по оси X: {dims.get('length', 3.0)}м
- Ширина по оси Y: {dims.get('width', 0.3)}м
- Высота по оси Z: {dims.get('height', 3.2)}м

ПРАВИЛА ГЕНЕРАЦИИ ГЕОМЕТРИИ (ВАЖНО):
1. Количество бревен в модуле: {params.get('logs_in_segment', 10)}. Они должны стоять вплотную друг к другу в один ряд вдоль оси X.
2. Диаметр каждого бревна: {params.get('log_diameter', 0.3)}м.
3. Каждое бревно — это вертикальный цилиндр (или куб, сглаженный фаской), верхняя часть которого (последние {float(params.get('sharpen_ratio', 0.25)) * 100}% высоты) должна сходиться в конус (заострение).
4. Примени легкую рандомизацию высоты для каждого бревна в пределах {params.get('variance_height', 0.3)}м, чтобы частокол выглядел реалистично, а не идеально ровно.
5. Не используй высокоуровневые операторы выделения bpy.ops. Все вершины и грани создавай через bmesh.
"""

    logging.info(
        "🧠 Шаг 3: Формирование промпта завершено. Инициализация Orchestrator..."
    )

    # Имитация конфигурации (в будущем загрузится из файла конфига)
    mock_config = {
        "llm": {"provider": "ollama", "model": "deepseek-coder-v2"},
        "blender": {"host": "127.0.0.1", "port": 9876},
    }

    orchestrator = Orchestrator(mock_config)

    logging.info("🚀 Шаг 4: Запуск процесса генерации ассета...")

    try:
        # Передаем промпт и категорию в оркестратор
        result = await orchestrator.generate_asset_workflow(
            prompt=prompt, category=asset_data.get("sub_category", "defense")
        )

        if result.get("status") == "success":
            logging.info("🎉 Тест завершен успешно! Проверь окно Blender.")
        else:
            logging.error(f"❌ Ошибка генерации: {result.get('message')}")

    except Exception as e:
        logging.error(f"💥 Критическая ошибка во время теста: {e}")
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    # Запуск асинхронного теста
    asyncio.run(test_palisade_generation())
