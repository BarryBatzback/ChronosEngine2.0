import logging
from pathlib import Path
from typing import Dict, Any

# Импорт наших очищенных сервисов
from services.llm_service import LLMService
from services.blender_service import BlenderService
from services.blender_api_helper import BlenderAPIHelper
from services.asset_factory import AssetFactory
from services.semantic_analyzer import SemanticAnalyzer


class Orchestrator:
    def __init__(self, config: Dict[str, Any]):
        self.root = Path(__file__).resolve().parent.parent
        self.config = config

        # Инициализация сервисов
        self.llm = LLMService(config.get("llm", {}))
        self.semantic = SemanticAnalyzer()
        self.blender = BlenderService(config.get("blender", {}))
        self.api_helper = BlenderAPIHelper()
        self.asset_factory = AssetFactory(self.root)

        logging.info("🚀 Chronos Orchestrator v2.0 initialized")

    async def generate_asset_workflow(self, prompt: str, category: str = "weapon"):
        """
        Главный рабочий процесс генерации ассета.
        """
        logging.info(f"📝 Processing prompt: {prompt}")

        # 1. Анализ промпта и получение 'сырого' кода от LLM
        system_hint = self.api_helper.get_api_hint(category)
        full_prompt = f"{system_hint}\n\nTask: {prompt}"

        raw_code = await self.llm.generate(full_prompt)

        # 2. Валидация и трансформация кода
        validation = self.api_helper.validate_and_fix_syntax(raw_code)

        if not validation["is_valid"]:
            logging.error(f"❌ LLM generated invalid code: {validation['errors']}")
            return {
                "status": "error",
                "message": "Syntax validation failed",
                "details": validation["errors"],
            }
        # prompt = self.semantic.enhance(prompt, category)

        if validation["suggestions"]:
            logging.warning(f"⚠️ API Suggestions: {validation['suggestions']}")

        # 3. Регистрация будущего ассета и подготовка UID
        asset_id = self.asset_factory.generate_uid("MSH")

        # 4. Обертка в безопасный Chronos-контекст (используем ОЧИЩЕННЫЙ код!)
        final_code = self.api_helper.wrap_in_chronos_context(
            validation[
                "cleaned_code"
            ],  # ← Здесь исправлено: cleaned_code, а не raw_code
            asset_id=asset_id,
        )

        # 5. Исполнение в Blender
        logging.info(f"🛠 Sending validated code to Blender for Asset: {asset_id}")
        result = await self.blender.run_python(final_code)

        if result.get("status") == "success":
            self.asset_factory.register_asset(
                asset_id, metadata={"category": category, "prompt": prompt}
            )
            logging.info(f"✅ Asset {asset_id} created and registered.")
            return {
                "status": "success",
                "asset_id": asset_id,
                "message": f"Asset {asset_id} generated successfully",
            }
        else:
            logging.error(f"❌ Blender execution failed: {result.get('message')}")
            return {
                "status": "error",
                "message": result.get("message", "Unknown error"),
                "asset_id": asset_id,
            }

    async def shutdown(self):
        """Корректное завершение работы"""
        await self.blender.close()
        logging.info("📴 Orchestrator shutdown.")
