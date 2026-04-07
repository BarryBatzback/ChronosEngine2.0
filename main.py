# main.py (чистая версия)
import sys
from pathlib import Path

# Добавляем корневой путь
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

import asyncio
from core.orchestrator import Orchestrator


async def main():
    orchestrator = Orchestrator()
    await orchestrator.run_cli()


if __name__ == "__main__":
    asyncio.run(main())
