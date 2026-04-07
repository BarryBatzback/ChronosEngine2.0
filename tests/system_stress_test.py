import asyncio
import time
import json
from datetime import datetime
from pathlib import Path
from loguru import logger

# Импортируем наш Оркестратор
from core.orchestrator import Orchestrator

# Настройка расширенного логирования в файл и консоль
LOG_FILE = Path("logs/test_runs.log")
LOG_FILE.parent.mkdir(exist_ok=True)

logger.add(
    LOG_FILE,
    rotation="10 MB",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)


class ChronosSystemTester:
    def __init__(self):
        # Имитация конфига (укажи свои рабочие модели)
        self.config = {
            "llm": {"model": "qwen2.5-coder:7b", "temperature": 0.1},  # или gemma2:9b
            "blender": {"host": "127.0.0.1", "port": 9876},
        }
        self.orchestrator = Orchestrator(self.config)
        self.results = []

    async def run_test_case(self, name: str, prompt: str, category: str):
        """Прогон одного тестового сценария с полным логированием цикла."""
        logger.info(f"🚀 ЗАПУСК ТЕСТА: [{name}]")
        start_time = time.time()

        test_report = {
            "test_name": name,
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "steps": [],
        }

        try:
            # Шаг 1: Отправка и генерация (LLM Stage)
            logger.debug(f"[{name}] Шаг 1: Запрос к LLM...")
            step_start = time.time()

            # Мы вызываем метод оркестратора, но добавим внутренний мониторинг
            result = await self.orchestrator.generate_asset_workflow(prompt, category)

            duration = round(time.time() - step_start, 2)
            test_report["total_duration"] = duration

            if result.get("status") == "success":
                logger.success(f"[{name}] ТЕСТ ПРОЙДЕН за {duration}с")
                test_report["status"] = "PASSED"
            else:
                logger.error(f"[{name}] ОШИБКА: {result.get('message')}")
                test_report["status"] = "FAILED"
                test_report["error_details"] = result.get("details")

        except Exception as e:
            logger.exception(f"[{name}] КРИТИЧЕСКИЙ СБОЙ СИСТЕМЫ: {e}")
            test_report["status"] = "CRASHED"
            test_report["error"] = str(e)

        self.results.append(test_report)
        return test_report

    async def run_full_suite(self):
        """Набор тестов разной сложности."""
        test_cases = [
            {
                "name": "Primitive Check",
                "prompt": "Create a simple low-poly wooden crate.",
                "category": "prop",
            },
            {
                "name": "Geometry Logic",
                "prompt": "Generate a sharp katana blade with a curved edge using bmesh operations.",
                "category": "weapon",
            },
            {
                "name": "Stress Math",
                "prompt": "Create a procedural spiral staircase with 15 steps, each rotated by 20 degrees.",
                "category": "architecture",
            },
        ]

        logger.info("=== НАЧАЛО СИСТЕМНОГО ТЕСТИРОВАНИЯ CHRONOS ENGINE ===")

        for case in test_cases:
            await self.run_test_case(case["name"], case["prompt"], case["category"])
            await asyncio.sleep(2)  # Пауза между тестами для очистки VRAM

        await self.orchestrator.shutdown()
        self.save_final_report()

    def save_final_report(self):
        """Сохранение итогового JSON отчета для аналитики."""
        report_path = Path("logs/final_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=4, ensure_ascii=False)
        logger.info(f"📊 Итоговый отчет сохранен в {report_path}")


if __name__ == "__main__":
    tester = ChronosSystemTester()
    asyncio.run(tester.run_full_suite())
