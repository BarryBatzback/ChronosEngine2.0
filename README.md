#  Game Asset Orchestrator

Локальная система генерации 3D-ассетов для игр на базе Qwen + Ollama + Blender + ComfyUI.

##  Быстрый старт

1. Установите Ollama: https://ollama.com
2. Запустите: \powershell -ExecutionPolicy Bypass -File scripts/setup_qwen.ps1\
3. Запустите: \python scripts/create_structure.ps1\
4. Запустите: \pip install -r requirements.txt\
5. Запустите: \python main.py\

##  Структура проекта

- \config/\ - Конфигурация
- \core/\ - Ядро системы
- \gents/\ - ИИ-агенты
- \services/\ - Внешние сервисы
- \lender_addon/\ - Аддон для Blender
- \workflows/\ - ComfyUI workflow
- \database/\ - База данных
- \output/\ - Сгенерированные ассеты

##  Требования

- Windows 10/11
- NVIDIA RTX 3060 16GB (или аналог)
- Python 3.10+
- Blender 4.2+
- ComfyUI
- Ollama + Qwen модели
