"""
Сервис для работы с LLM (DeepSeek via Ollama)
Полностью локальная реализация без API ключей
"""

import ollama
import asyncio
import json
import re
from typing import Dict, Any, Optional, List
from loguru import logger


class LLMService:
    """Сервис для работы с DeepSeek через Ollama"""
    
    def __init__(self, config: Dict):
        self.provider = config.get('provider', 'ollama')
        self.host = config.get('host', 'http://localhost')
        self.port = config.get('port', 11434)
        self.base_url = f"{self.host}:{self.port}"
        
        # DeepSeek модели (быстрее)
        self.model_coordinator = config.get('model_coordinator', 'deepseek-coder:6.7b')
        self.model_specialist = config.get('model_specialist', 'deepseek-coder:6.7b')
        self.model_vision = config.get('model_vision', 'deepseek-coder:6.7b')
        
        self.temperature = config.get('temperature', 0.3)
        self.max_tokens = config.get('max_tokens', 4096)
        self.num_ctx = config.get('num_ctx', 8192)
        self.keep_alive = config.get('keep_alive', '5m')
        self.num_gpu = config.get('num_gpu', 1)
        
        # Проверка подключения к Ollama
        if not self._check_connection():
            logger.warning("⚠️ Ollama not running. Please start Ollama first.")
        
        logger.info(f"🤖 LLMService initialized with DeepSeek (Ollama)")
        logger.info(f"   Coordinator: {self.model_coordinator}")
        logger.info(f"   Specialist: {self.model_specialist}")
    
    def _check_connection(self) -> bool:
        """Проверка подключения к Ollama"""
        try:
            client = ollama.Client(host=self.base_url)
            client.list()
            return True
        except Exception as e:
            logger.error(f"❌ Ollama connection failed: {e}")
            return False
    
    def _get_client(self) -> ollama.Client:
        """Создание клиента Ollama"""
        return ollama.Client(host=self.base_url)
    
    async def generate(
        self, 
        prompt: str, 
        use_coordinator: bool = True,
        system_instruction: Optional[str] = None,
        stream: bool = False
    ):
        """Генерация текста через DeepSeek"""
        try:
            client = self._get_client()
            model = self.model_coordinator if use_coordinator else self.model_specialist
            
            messages = []
            
            if system_instruction:
                messages.append({
                    'role': 'system',
                    'content': system_instruction
                })
            
            messages.append({
                'role': 'user',
                'content': prompt
            })
            
            logger.debug(f"📤 Sending to {model}: {prompt[:100]}...")
            
            loop = asyncio.get_event_loop()
            
            if stream:
                async def stream_generator():
                    response = await loop.run_in_executor(
                        None,
                        lambda: client.chat(
                            model=model,
                            messages=messages,
                            stream=True,
                            options={
                                'temperature': self.temperature,
                                'num_predict': self.max_tokens,
                                'num_ctx': self.num_ctx,
                                'num_gpu': self.num_gpu,
                                'keep_alive': self.keep_alive
                            }
                        )
                    )
                    for chunk in response:
                        yield chunk['message']['content']
                return stream_generator()
            else:
                response = await loop.run_in_executor(
                    None,
                    lambda: client.chat(
                        model=model,
                        messages=messages,
                        stream=False,
                        options={
                            'temperature': self.temperature,
                            'num_predict': self.max_tokens,
                            'num_ctx': self.num_ctx,
                            'num_gpu': self.num_gpu,
                            'keep_alive': self.keep_alive
                        }
                    )
                )
                
                content = response['message']['content']
                logger.debug(f"📥 Received from {model}: {content[:100]}...")
                return content
                
        except Exception as e:
            logger.error(f"❌ LLM generation failed: {e}")
            raise
    
    async def generate_json(
        self, 
        prompt: str, 
        schema: Optional[Dict] = None,
        use_coordinator: bool = True
    ) -> Dict:
        """Генерация JSON ответа"""
        system_instruction = """
        You are a JSON API. Respond ONLY with valid JSON.
        Do not include markdown, explanations, or any other text.
        Do not wrap in ```json blocks.
        """
        
        if schema:
            system_instruction += f"\nExpected schema: {json.dumps(schema)}"
        
        response_text = await self.generate(
            prompt,
            use_coordinator=use_coordinator,
            system_instruction=system_instruction
        )
        
        response_text = self._clean_json_response(response_text)
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parse error: {e}")
            return await self._retry_json_parse(response_text, schema)
    
    # services/llm_service.py (дополните _clean_json_response)
    def _clean_json_response(self, text: str) -> str:
        """Очистка JSON от markdown и лишнего текста"""
        # Удаляем markdown-обёртки
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Удаляем объяснения до и после JSON
        text = re.sub(r'^.*?(\{)', r'\1', text, flags=re.DOTALL)
        text = re.sub(r'(\}).*?$', r'\1', text, flags=re.DOTALL)
        
        # Исправляем распространенные ошибки LLM
        text = re.sub(r",\s*}", "}", text)  # Висящие запятые
        text = re.sub(r",\s*]", "]", text)  # Висящие запятые в массивах
        
        # Находим первую { и последнюю }
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
        
        return text.strip()
    
    async def _retry_json_parse(self, raw_response: str, schema: Optional[Dict]) -> Dict:
        """Попытка исправить невалидный JSON через LLM"""
        try:
            fix_prompt = f"""
            The following JSON is invalid. Fix it and return only valid JSON.
            
            Raw response:
            {raw_response[:2000]}
            
            Return only the corrected JSON, no explanations.
            """
            
            fixed_text = await self.generate(
                fix_prompt,
                use_coordinator=False,
                system_instruction="You are a JSON fixer. Return only valid JSON."
            )
            
            fixed_text = self._clean_json_response(fixed_text)
            return json.loads(fixed_text)
            
        except Exception as e:
            logger.error(f"❌ JSON retry failed: {e}")
            return {'error': 'Failed to parse JSON', 'raw': raw_response[:500]}
    
    async def generate_code(
        self, 
        prompt: str, 
        language: str = "python"
    ) -> str:
        """Генерация кода (DeepSeek Coder оптимизирован для этого)"""
        system_instruction = f"""
        You are an expert {language} developer with deep knowledge of Blender API.
        Write clean, production-ready code with proper error handling.
        Include comments for complex logic.
        
        CRITICAL: Use ONLY modern Blender 3.0+ API:
        - Materials: use_nodes = True, ShaderNodeTexNoise, ShaderNodeValToRGB
        - NEVER use bpy.data.textures (deprecated)
        - NEVER use material.diffuse_color directly
        
        Return ONLY raw code, no markdown blocks, no explanations.
        """
        
        return await self.generate(
            prompt,
            use_coordinator=False,
            system_instruction=system_instruction
        )
    
    async def analyze_image(
        self, 
        image_path: str, 
        prompt: str
    ) -> str:
        """Анализ изображения (если есть vision модель)"""
        try:
            client = self._get_client()
            
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.chat(
                    model=self.model_vision,
                    messages=[{
                        'role': 'user',
                        'content': prompt,
                        'images': [image_data]
                    }],
                    options={
                        'temperature': self.temperature,
                        'num_predict': self.max_tokens,
                        'num_ctx': self.num_ctx
                    }
                )
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"❌ Image analysis failed: {e}")
            raise
    
    async def check_models(self) -> List[str]:
        """Проверка доступных моделей"""
        try:
            client = self._get_client()
            models = client.list()
            return [m['name'] for m in models.get('models', [])]
        except Exception as e:
            logger.error(f"❌ Failed to list models: {e}")
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        """Загрузка модели"""
        try:
            client = self._get_client()
            client.pull(model_name)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to pull model: {e}")
            return False