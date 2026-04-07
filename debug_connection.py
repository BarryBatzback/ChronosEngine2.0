import asyncio
import websockets
import json


async def test():
    uri = "ws://localhost:9876"
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connection successful!")
            await websocket.send(
                json.dumps(
                    {"type": "run_python", "code": "print('Hello from Python!')"}
                )
            )
            response = await websocket.recv()
            print(f"Response: {response}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")


asyncio.run(test())
