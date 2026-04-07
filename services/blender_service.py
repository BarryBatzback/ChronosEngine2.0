from loguru import logger
import websockets
import asyncio
import json


class BlenderService:
    def __init__(self, config: dict):
        # Используем 127.0.0.1 вместо localhost для надежности на Windows
        self.host = config.get("host", "127.0.0.1")
        self.port = config.get("port", 9876)
        self.uri = f"ws://{self.host}:{self.port}"
        self.websocket = None
        logger.info(f"🔌 BlenderService initialized: {self.uri}")

    async def connect(self):
        if self.websocket and not self.websocket.closed:
            return True

        try:
            # КРИТИЧЕСКИЙ МОМЕНТ: Отключаем пинги, чтобы сокет не закрывался
            # пока Ollama генерирует тяжелый код.
            self.websocket = await websockets.connect(
                self.uri, ping_interval=None, ping_timeout=None, close_timeout=10
            )
            logger.info("✅ Connected to Blender WebSocket server")
            return True
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False

    async def run_python(self, code: str):
        # Проверка и переподключение
        if not self.websocket or self.websocket.closed:
            connected = await self.connect()
            if not connected:
                return {"status": "error", "message": "Blender unreachable"}

        try:
            payload = json.dumps({"action": "run_python", "code": code})
            await self.websocket.send(payload)

            # Ждем ответа от Blender (30 секунд обычно хватает)
            response = await asyncio.wait_for(self.websocket.recv(), timeout=30.0)
            return json.loads(response)
        except asyncio.TimeoutError:
            logger.warning("⏳ Blender response timeout")
            return {"status": "error", "message": "Timeout waiting for Blender"}
        except Exception as e:
            logger.error(f"❌ Socket error: {e}")
            self.websocket = None
            return {"status": "error", "message": str(e)}

    async def close(self):
        if self.websocket:
            await self.websocket.close()
