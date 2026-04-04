# create_structure.ps1
# Скрипт создает полную структуру проекта Game Asset Orchestrator

Write-Host "=== Создание структуры проекта ===" -ForegroundColor Cyan

$root = Get-Location
$dirs = @(
    "config",
    "core",
    "agents",
    "services",
    "blender_addon",
    "workflows",
    "database",
    "logs",
    "output/characters",
    "output/environment",
    "output/props",
    "output/buildings",
    "output/comfyui",
    "tests",
    "scripts",
    "docs"
)

# Создание директорий
foreach ($dir in $dirs) {
    $path = Join-Path $root $dir
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Force -Path $path | Out-Null
        Write-Host "✓ Создано: $dir" -ForegroundColor Green
    }
    else {
        Write-Host "⚠ Существует: $dir" -ForegroundColor Yellow
    }
}

# Создание файлов с содержимым
$files = @{
    "config/settings.yaml" = @"
system:
  name: "GameAssetOrchestrator"
  version: "1.0.0"
  debug: false

gpu:
  vram_limit_gb: 14
  cuda_version: "12.4"

blender:
  version: "4.2"
  host: "localhost"
  port: 9876
  auto_save: true

comfyui:
  host: "localhost"
  port: 8188
  api_port: 8188
  workflows_path: "./workflows"
  output_path: "./output/comfyui"

llm:
  provider: "ollama"
  host: "http://localhost"
  port: 11434
  model_coordinator: "qwen2.5:14b"
  model_specialist: "qwen2.5:7b"
  model_vision: "qwen2.5-vl:7b"
  temperature: 0.3
  max_tokens: 4096
  num_ctx: 8192

database:
  type: "sqlite"
  path: "./database/orchestrator.db"

logging:
  level: "INFO"
  file: "./logs/orchestrator.log"
  max_size_mb: 100
  backup_count: 5
"@

    "config/.env"          = @"
OLLAMA_HOST=http://localhost:11434
BLENDER_PATH=C:/Program Files/Blender Foundation/Blender 4.2/blender.exe
COMFYUI_PATH=C:/AI/ComfyUI_windows_portable
PROJECT_ROOT=$root
OUTPUT_PATH=$root/output
"@

    "requirements.txt"     = @"
python-dotenv==1.0.0
pyyaml==6.0.1
pydantic==2.5.0
pydantic-settings==2.1.0
ollama==0.1.7
sqlalchemy==2.0.23
alembic==1.13.0
fastapi==0.109.0
uvicorn==0.25.0
httpx==0.26.0
websockets==12.0
loguru==0.7.2
rich==13.7.0
tqdm==4.66.1
Pillow==10.2.0
pytest==7.4.4
pytest-asyncio==0.23.3
"@

    ".gitignore"           = @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/*.log

# Database
database/*.db

# Output
output/*
!output/.gitkeep

# Models
*.ckpt
*.safetensors
*.pth

# OS
.DS_Store
Thumbs.db
"@

    "README.md"            = @"
# 🎮 Game Asset Orchestrator

Локальная система генерации 3D-ассетов для игр на базе Qwen + Ollama + Blender + ComfyUI.

## 🚀 Быстрый старт

1. Установите Ollama: https://ollama.com
2. Запустите: \`powershell -ExecutionPolicy Bypass -File scripts/setup_qwen.ps1\`
3. Запустите: \`python scripts/create_structure.ps1\`
4. Запустите: \`pip install -r requirements.txt\`
5. Запустите: \`python main.py\`

## 📁 Структура проекта

- \`config/\` - Конфигурация
- \`core/\` - Ядро системы
- \`agents/\` - ИИ-агенты
- \`services/\` - Внешние сервисы
- \`blender_addon/\` - Аддон для Blender
- \`workflows/\` - ComfyUI workflow
- \`database/\` - База данных
- \`output/\` - Сгенерированные ассеты

## 🛠 Требования

- Windows 10/11
- NVIDIA RTX 3060 16GB (или аналог)
- Python 3.10+
- Blender 4.2+
- ComfyUI
- Ollama + Qwen модели
"@

    "main.py"              = @"
#!/usr/bin/env python
"""
Game Asset Orchestrator - Точка входа
"""

import asyncio
from core.orchestrator import Orchestrator

async def main():
    orchestrator = Orchestrator()
    await orchestrator.run_cli()

if __name__ == "__main__":
    asyncio.run(main())
"@

    "core/__init__.py"     = ""
    "agents/__init__.py"   = ""
    "services/__init__.py" = ""
    "database/__init__.py" = ""
    "tests/__init__.py"    = ""
}

foreach ($file in $files.Keys) {
    $path = Join-Path $root $file
    $directory = Split-Path $path -Parent
    
    if (-not (Test-Path $directory)) {
        New-Item -ItemType Directory -Force -Path $directory | Out-Null
    }
    
    if (-not (Test-Path $path)) {
        Set-Content -Path $path -Value $files[$file] -Encoding UTF8
        Write-Host "✓ Создано: $file" -ForegroundColor Green
    }
    else {
        Write-Host "⚠ Существует: $file" -ForegroundColor Yellow
    }
}

Write-Host "`n=== Структура создана успешно! ===" -ForegroundColor Green
Write-Host "`n📝 Следующие шаги:" -ForegroundColor Cyan
Write-Host "  1. pip install -r requirements.txt"
Write-Host "  2. powershell -File scripts/setup_qwen.ps1"
Write-Host "  3. python main.py"