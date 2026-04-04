import asyncio
from loguru import logger
from rich.console import Console
from rich.panel import Panel
import yaml

# Импорты твоих сервисов
from services.llm_service import LLMService
from services.blender_service import BlenderService
from services.blender_knowledge_base import BlenderKnowledgeBase
from agents.geometry_agent import GeometryAgent

class Orchestrator:
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.console = Console()
        self.config = self._load_config(config_path)

        # Инициализация сервисов
        self.llm = LLMService(self.config.get('llm', {}))
        self.blender = BlenderService(self.config.get('blender', {}))
        self.kb = BlenderKnowledgeBase()

        # Инициализация агентов
        self.geometry_agent = GeometryAgent(self.llm, self.blender, self.kb)

        logger.info("🎯 Orchestrator v1.0 запущен и готов к работе")

    def _load_config(self, path: str) -> dict:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception:
            # Дефолтный конфиг, если файла нет
            return {
                'llm': {'model_coordinator': 'deepseek-coder:6.7b'},
                'blender': {'host': '127.0.0.1', 'port': 9876}
            }

    async def generate_from_reference(self, prompt: str, material: str):
        # 1. Запуск Hunyuan3D (Вариант 2)
        print(f"🎨 Генерирую форму через Hunyuan3D для: {prompt}")
        # Тут будет вызов ComfyUI API с твоим .json воркфлоу
        
        # 2. Получение настроек материала (Вариант 3)
        mat_props = self.reference_service.get_material_blueprint(material)
        
        # 3. Формирование задания для GeometryAgent
        refinement_task = f"""
        Импортируй сгенерированный меш. 
        Примени материал с параметрами: {mat_props}.
        Исправь масштаб согласно историческим данным 9 века.
        """
        return await self.agents['geometry'].execute(refinement_task)


    async def handle_user_request(self, prompt: str):
        if not await self.blender.connect():
            self.console.print("[red]❌ Ошибка связи с Blender[/]")
            return

        result = await self.geometry_agent.execute({"prompt": prompt}, "session_1")

        if result.get('success'):
            self.console.print(f"\n[green]✅ Готово![/] {result['message']}")
        else:
            self.console.print(f"\n[red]❌ Сбой:[/ ] {result['message']}")

    async def run_cli(self):
        self.console.print(Panel.fit(
            "🎮 [bold cyan]Chronos Engine 2.0[/]\n"
            "Интерфейс управления ИИ-генерацией ассетов\n"
            "Порт Blender: 9876 | Модель: DeepSeek",
            border_style="magenta"
        ))

        while True:
            try:
                user_input = self.console.input("\n[bold blue]🎨 Запрос (или 'exit'):[/] ").strip()

                if user_input.lower() in ['exit', 'quit']:
                    break
                
                if not user_input:
                    continue

                self.console.print("[yellow]⏳ Работаю над ассетом...[/]")
                await self.handle_user_request(user_input)

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Ошибка в цикле CLI: {e}")

async def main():
    orchestrator = Orchestrator()
    await orchestrator.run_cli()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass