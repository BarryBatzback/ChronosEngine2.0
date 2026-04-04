# test_integration.py
import asyncio
import json
import re
import websockets
import yaml
from services.llm_service import LLMService

# Настройки
BLENDER_URI = "ws://127.0.0.1:9876"
CONFIG_PATH = "config/settings.yaml"

async def send_to_blender(code: str) -> dict:
    """Отправляет Python-код в Blender через WebSocket"""
    try:
        async with websockets.connect(BLENDER_URI) as websocket:
            command = {
                'action': 'run_python',
                'args': {'code': code}
            }
            await websocket.send(json.dumps(command))
            response = await websocket.recv()
            return json.loads(response)
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def clean_code(code: str) -> str:
    """
    Надёжная очистка кода от Markdown-разметки.
    Извлекает первый блок кода, игнорируя текст до и после него.
    """
    code = code.strip()
    pattern = r'```(?:python)?\s*(.*?)\s*```'
    match = re.search(pattern, code, re.DOTALL)
    if match:
        return match.group(1).strip()
    return code

async def main():
    print("🚀 Запуск интеграционного теста: LLM -> Blender\n")
    
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Config file not found: {CONFIG_PATH}")
        return

    try:
        llm = LLMService(config['llm'])
        print(f"🤖 LLM готов: {config['llm']['model_specialist']}")
    except Exception as e:
        print(f"❌ LLM init error: {e}")
        return
    
    user_prompt = "Создай в Blender красный куб размером 2 метра в центре сцены и синюю сферу рядом с ним."
    print(f"📝 Запрос: {user_prompt}\n")
    
    print("⏳ Генерация кода через LLM...")
    code_prompt = f"""
Напиши Python-код для Blender (bpy), который выполняет:
{user_prompt}

Требования:
- Используй bpy.ops и bpy.data
- Добавь материалы (красный для куба, синий для сферы)
- Код должен быть готов к выполнению
- Не используй функции, пиши прямой код
"""
    try:
        raw_code = await llm.generate_code(code_prompt)
        code = clean_code(raw_code)
        
        print(f"📄 Сгенерированный код:\n{code}\n")
        
        if '```' in code:
            print("⚠️ Warning: Markdown markers still present!")
            
    except Exception as e:
        print(f"❌ LLM generation error: {e}")
        return
    
    print("📤 Отправка кода в Blender...")
    result = await send_to_blender(code)
    
    if result.get('status') == 'ok':
        print("✅ Успех! Объекты созданы в Blender.")
        print(f"📋 Ответ: {result.get('message')}")
    else:
        print("❌ Ошибка в Blender:")
        print(f"📋 {result.get('message')}")
        if 'trace' in result:
            print(f"🔍 Traceback:\n{result['trace']}")

if __name__ == "__main__":
    asyncio.run(main())