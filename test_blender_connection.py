# test_blender_connection.py
import asyncio
import websockets
from loguru import logger

async def test_blender_connection():
    try:
        async with websockets.connect('ws://localhost:9876') as websocket:
            # Test command
            test_command = {
                "type": "run_python",
                "code": "print('✅ WebSocket connection test successful!')"
            }
            
            await websocket.send(json.dumps(test_command))
            response = await websocket.recv()
            print("📡 Blender response:", response)
            
    except Exception as e:
        print("❌ Connection failed:", e)

if __name__ == "__main__":
    import json
    asyncio.run(test_blender_connection())
