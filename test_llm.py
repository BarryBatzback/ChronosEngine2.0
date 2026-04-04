# test_llm.py
import asyncio
import yaml
from services.llm_service import LLMService

async def test_llm():
    # Загрузка конфигурации из settings.yaml
    config_path = "config/settings.yaml"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        llm_config = config_data.get('llm', {})
        print(f"Loaded LLM config: {llm_config.get('model_coordinator', 'N/A')}, {llm_config.get('model_specialist', 'N/A')}")
        
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_path}")
        return
    except yaml.YAMLError as e:
        print(f"❌ Error parsing YAML: {e}")
        return

    # Создание экземпляра LLMService
    try:
        llm_service = LLMService(llm_config)
    except Exception as e:
        print(f"❌ Error initializing LLMService: {e}")
        return

    # Проверим подключение
    print("\n--- Checking LLM Health ---")
    try:
        health = await llm_service.health_check()
        print(f"LLM Health: {health}")
    except Exception as e:
        print(f"LLM Health Check Error: {e}")

    # Проверим генерацию текста
    print("\n--- Testing Text Generation ---")
    try:
        response = await llm_service.generate("Привет! Кто ты?", use_coordinator=True)
        print(f"LLM Response: {response[:200]}...") # Выводим первые 200 символов
    except Exception as e:
        print(f"LLM Generation Error: {e}")

    # Проверим генерацию кода (важно для Blender)
    print("\n--- Testing Code Generation ---")
    try:
        code_prompt = "Напиши Python-код для Blender (bpy), который создает куб в центре сцены."
        code_response = await llm_service.generate_code(code_prompt)
        print(f"LLM Generated Code Preview:\n{code_response[:300]}...") # Выводим первые 300 символов
    except Exception as e:
        print(f"LLM Code Generation Error: {e}")

    # Проверим генерацию JSON (для планирования)
    print("\n--- Testing JSON Generation ---")
    try:
        json_prompt = "Опиши простой 3D-объект 'красный куб'. Верни JSON с полями: 'type', 'color', 'size'."
        json_response = await llm_service.generate_json(json_prompt)
        print(f"LLM Generated JSON: {json_response}")
    except Exception as e:
        print(f"LLM JSON Generation Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm())