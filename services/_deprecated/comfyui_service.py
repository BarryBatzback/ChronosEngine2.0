"""
Сервис для работы с ComfyUI API
Генерация 3D-моделей через Hunyuan3D
"""

import json
import time
import requests
import os
import websocket
import uuid
from typing import Dict, Any, Optional
from loguru import logger


class ComfyUIService:
    """Сервис для генерации 3D-моделей через ComfyUI"""

    def __init__(self, config: Dict = None):
        if config is None:
            config = {}
        self.base_url = config.get("base_url", "http://127.0.0.1:8188")
        self.client_id = str(uuid.uuid4())
        self.output_dir = config.get("output_dir", "./output/3d_models")
        self.timeout = config.get("timeout", 300)
        self.ws = None

        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"🎨 ComfyUIService initialized: {self.base_url}")

    def check_health(self) -> bool:
        """Проверка доступности ComfyUI"""
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ ComfyUI not available: {e}")
            return False

    def queue_prompt(self, workflow: Dict) -> Optional[str]:
        """Отправка workflow в очередь ComfyUI"""
        try:
            payload = {"prompt": workflow, "client_id": self.client_id}
            response = requests.post(
                f"{self.base_url}/prompt", json=payload, timeout=30
            )
            if response.status_code == 200:
                prompt_id = response.json().get("prompt_id")
                logger.info(f"⏳ Prompt queued: {prompt_id}")
                return prompt_id
            else:
                logger.error(f"Failed to queue: {response.text}")
                return None
        except Exception as e:
            logger.error(f"❌ Queue error: {e}")
            return None

    def wait_for_completion(self, prompt_id: str) -> Optional[Dict]:
        """Ожидание завершения генерации через WebSocket"""
        ws_url = self.base_url.replace("http", "ws") + "/ws"
        try:
            self.ws = websocket.WebSocket()
            self.ws.connect(ws_url)
            self.ws.send(json.dumps({"type": "status"}))

            start_time = time.time()
            while time.time() - start_time < self.timeout:
                out = self.ws.recv()
                if isinstance(out, bytes):
                    continue

                data = json.loads(out)
                if data.get("type") == "executing":
                    node = data.get("data", {}).get("node")
                    if node is None:
                        # Генерация завершена
                        return self.get_history(prompt_id)

                time.sleep(0.5)

            logger.error(f"❌ Timeout waiting for completion")
            return None

        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
            return None
        finally:
            if self.ws:
                self.ws.close()

    def get_history(self, prompt_id: str) -> Optional[Dict]:
        """Получение истории выполнения"""
        try:
            response = requests.get(f"{self.base_url}/history/{prompt_id}")
            if response.status_code == 200:
                history = response.json()
                if prompt_id in history:
                    return history[prompt_id]
            return None
        except Exception as e:
            logger.error(f"❌ History error: {e}")
            return None

    def get_output_file(self, history: Dict) -> Optional[str]:
        """Извлечение пути к выходному GLB файлу"""
        outputs = history.get("outputs", {})
        for node_id, node_output in outputs.items():
            if "3d" in node_output:
                for item in node_output["3d"]:
                    if item.get("type") == "glb":
                        filename = item.get("filename")
                        subfolder = item.get("subfolder", "")
                        filepath = os.path.join(
                            self.output_dir, f"model_{int(time.time())}.glb"
                        )
                        # Скачиваем файл
                        download_url = f"{self.base_url}/view?filename={filename}&subfolder={subfolder}&type=output"
                        response = requests.get(download_url)
                        if response.status_code == 200:
                            with open(filepath, "wb") as f:
                                f.write(response.content)
                            logger.info(f"📥 Model saved: {filepath}")
                            return filepath
        return None

    def generate_from_text(self, prompt: str, workflow: Dict = None) -> Optional[str]:
        """Генерация 3D-модели из текста"""
        try:
            # Модифицируем workflow с текстовым промптом
            workflow = self._inject_text_prompt(workflow or {}, prompt)

            # Отправляем в очередь
            prompt_id = self.queue_prompt(workflow)
            if not prompt_id:
                return None

            # Ожидаем завершения
            history = self.wait_for_completion(prompt_id)
            if not history:
                return None

            # Получаем файл
            return self.get_output_file(history)

        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            return None

    def _inject_text_prompt(self, workflow: Dict, prompt: str) -> Dict:
        """Внедрение текстового промпта в workflow"""
        for node_id, node in workflow.items():
            if node.get("class_type") == "CLIPTextEncode":
                node["inputs"]["text"] = prompt
                logger.debug(f"📝 Injected prompt into node {node_id}")
                break
        return workflow

    def import_to_blender(self, glb_path: str) -> Dict[str, Any]:
        """Генерация кода для импорта GLB в Blender"""
        import_code = f"""
import bpy
import os

# Очистка сцены
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Импорт GLB модели
glb_path = r"{glb_path}"
bpy.ops.import_scene.gltf(filepath=glb_path)

print(f"✅ Model imported from {{glb_path}}")
print(f"📊 Objects in scene: {{len(bpy.context.scene.objects)}}")
"""
        return {"status": "ok", "code": import_code, "file_path": glb_path}

    async def run_python(self, code: str):
        # Если соединение упало (timeout), пытаемся подключиться заново перед отправкой
        if not self.websocket or self.websocket.closed:
            logger.info("🔌 Reconnecting to Blender...")
            await self.connect()

        if not self.websocket:
            return {"status": "error", "message": "Blender not connected"}

        payload = {"action": "run_python", "code": code}
        await self.websocket.send(json.dumps(payload))
