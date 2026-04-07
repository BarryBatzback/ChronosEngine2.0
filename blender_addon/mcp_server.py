bl_info = {
    "name": "Chronos MCP Server",
    "author": "Chronos Engine",
    "version": (1, 2),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > Chronos",
    "description": "MCP Server for AI-driven 3D generation with output capture",
    "category": "Interface",
}

import bpy
import asyncio
import json
import traceback
import threading
from bpy.types import Panel, Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty
import logging

logging.basicConfig(level=logging.INFO)

# Импорты для перехвата вывода
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

mcp_server = None


class BlenderMCPServer:
    async def handle_run_python(self, data):
        """Выполняет Python код и возвращает вывод"""
        code = data.get("code", "")

        # Создаем контекст для перехвата вывода
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        result = {
            "status": "ok",
            "message": "Code executed successfully",
            "output": "",
            "error": "",
        }

        try:
            # Перехватываем stdout и stderr
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Выполняем код в глобальном контексте Blender
                exec(code, {"bpy": bpy, "__builtins__": __builtins__, "sys": sys})

            # Получаем вывод
            result["output"] = stdout_capture.getvalue()
            result["error"] = stderr_capture.getvalue()

        except Exception as e:
            result["status"] = "error"
            result["message"] = str(e)
            result["error"] = stderr_capture.getvalue() + traceback.format_exc()

        return result


class MCPServer:
    def __init__(self, host="127.0.0.1", port=9876):
        self.host = host
        self.port = port
        self.loop = None
        self.thread = None
        self.server = None
        self.running = False
        self.websockets = None
        self.blender_handler = BlenderMCPServer()

    def ensure_websockets(self):
        try:
            import websockets

            self.websockets = websockets
            print("✅ websockets module loaded")
            return True
        except ImportError as e:
            print(f"❌ websockets not installed: {e}")
            return False

    async def handle_client(self, websocket):
        """Обработчик подключения клиента"""
        print(f"✅ Client connected from {websocket.remote_address}")
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    action = data.get("action")
                    print(f"📨 Received action: {action}")

                    # Обрабатываем команды
                    if action == "run_python":
                        result = await self.blender_handler.handle_run_python(data)
                    elif action == "get_scene_data":
                        result = await self.execute_command(data)
                    elif action == "health_check":
                        result = {"status": "ok", "message": "Server is healthy"}
                    else:
                        result = {
                            "status": "error",
                            "message": f"Unknown action: {action}",
                        }

                    await websocket.send(json.dumps(result))
                    print(f"📤 Sent response for {action}")

                except Exception as e:
                    error_msg = {
                        "status": "error",
                        "message": f"Message processing error: {str(e)}",
                        "trace": traceback.format_exc(),
                    }
                    await websocket.send(json.dumps(error_msg))
                    print(f"❌ Message error: {e}")

        except Exception as e:
            print(f"❌ Client handler error: {e}")
        finally:
            print(f"❌ Client disconnected")

    async def execute_command(self, data):
        """Выполняет команду в основном потоке Blender"""
        future = asyncio.get_event_loop().create_future()

        def run_in_main():
            try:
                action = data.get("action")

                if action == "get_scene_data":
                    objects = []
                    for obj in bpy.context.scene.objects:
                        objects.append(
                            {
                                "name": obj.name,
                                "type": obj.type,
                                "location": list(obj.location),
                                "rotation": list(obj.rotation_euler),
                                "scale": list(obj.scale),
                            }
                        )
                    result = {"status": "ok", "data": {"objects": objects}}

                else:
                    result = {"status": "error", "message": f"Unknown action: {action}"}

            except Exception as e:
                result = {
                    "status": "error",
                    "message": str(e),
                    "trace": traceback.format_exc(),
                }

            if not future.done():
                self.loop.call_soon_threadsafe(future.set_result, result)

        # Запускаем в главном потоке Blender
        bpy.app.timers.register(lambda: (run_in_main(), None)[0], first_interval=0.0)

        try:
            return await asyncio.wait_for(future, timeout=30.0)
        except asyncio.TimeoutError:
            return {"status": "error", "message": "Command execution timeout"}

    async def start_server(self):
        if not self.ensure_websockets():
            return

        print(f"🚀 Starting MCP Server on {self.host}:{self.port}")
        try:
            self.server = await self.websockets.serve(
                self.handle_client, self.host, self.port
            )
            self.running = True
            print(f"✅ Server running on ws://{self.host}:{self.port}")
            await self.server.wait_closed()
        except Exception as e:
            print(f"❌ Server start failed: {e}")
            self.running = False

    def _run_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.start_server())
        except Exception as e:
            print(f"❌ Server error: {e}")
            self.running = False

    def start(self):
        if self.running:
            print("⚠️ Server already running")
            return False

        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

        # Ждем немного инициализации
        import time

        time.sleep(1)
        return self.running

    def stop(self):
        if self.server and self.running:
            print("🛑 Stopping server...")

            async def shutdown():
                self.server.close()
                await self.server.wait_closed()
                self.running = False
                print("✅ Server stopped")

            if self.loop and self.loop.is_running():
                asyncio.run_coroutine_threadsafe(shutdown(), self.loop)
            else:
                self.running = False
        else:
            self.running = False


# ============================================================
# UI Panel
# ============================================================
class CHRONOS_PT_MCP(Panel):
    bl_label = "Chronos MCP Server"
    bl_idname = "CHRONOS_PT_MCP"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Chronos"

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons[__name__].preferences

        layout.prop(prefs, "host")
        layout.prop(prefs, "port")
        layout.separator()

        global mcp_server
        if mcp_server and mcp_server.running:
            layout.label(text="Status: 🟢 RUNNING", icon="CHECKMARK")
            layout.label(text=f"URL: ws://{prefs.host}:{prefs.port}")
            layout.operator("chronos.stop_server", text="Stop Server", icon="X")
        else:
            layout.label(text="Status: 🔴 STOPPED", icon="CANCEL")
            layout.operator("chronos.start_server", text="Start Server", icon="PLAY")


class CHRONOS_OT_StartServer(Operator):
    bl_idname = "chronos.start_server"
    bl_label = "Start MCP Server"
    bl_description = "Start WebSocket server for AI communication"

    def execute(self, context):
        global mcp_server
        prefs = context.preferences.addons[__name__].preferences

        if mcp_server is None:
            mcp_server = MCPServer(host=prefs.host, port=prefs.port)

        if mcp_server.start():
            self.report({"INFO"}, f"MCP Server started on {prefs.host}:{prefs.port}")
        else:
            self.report({"ERROR"}, "Failed to start server")
        return {"FINISHED"}


class CHRONOS_OT_StopServer(Operator):
    bl_idname = "chronos.stop_server"
    bl_label = "Stop MCP Server"
    bl_description = "Stop WebSocket server"

    def execute(self, context):
        global mcp_server
        if mcp_server:
            mcp_server.stop()
            mcp_server = None
            self.report({"INFO"}, "MCP Server stopped")
        else:
            self.report({"WARNING"}, "Server was not running")
        return {"FINISHED"}


class CHRONOS_AddonPreferences(AddonPreferences):
    bl_idname = __name__
    host: StringProperty(
        name="Host", default="127.0.0.1", description="IP address to bind the server"
    )
    port: IntProperty(
        name="Port",
        default=9876,
        min=1024,
        max=65535,
        description="Port number for WebSocket server",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "host")
        layout.prop(self, "port")
        layout.separator()
        layout.label(text="WebSocket Server Settings", icon="NETWORK_DRIVE")


# ============================================================
# Registration
# ============================================================
classes = (
    CHRONOS_AddonPreferences,
    CHRONOS_PT_MCP,
    CHRONOS_OT_StartServer,
    CHRONOS_OT_StopServer,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    print("✅ Chronos MCP Server addon registered")


def unregister():
    global mcp_server
    if mcp_server:
        mcp_server.stop()
        mcp_server = None

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("✅ Chronos MCP Server addon unregistered")


# Автозапуск сервера при включении аддона
@bpy.app.handlers.persistent
def auto_start_server(dummy):
    global mcp_server
    try:
        prefs = bpy.context.preferences.addons[__name__].preferences
        mcp_server = MCPServer(host=prefs.host, port=prefs.port)
        if mcp_server.start():
            print("✅ MCP Server auto-started")
        else:
            print("❌ MCP Server auto-start failed")
    except:
        print("⚠️ Could not auto-start MCP Server")


def register_handlers():
    bpy.app.handlers.load_post.append(auto_start_server)


def unregister_handlers():
    bpy.app.handlers.load_post.remove(auto_start_server)


if __name__ == "__main__":
    register()
    register_handlers()
