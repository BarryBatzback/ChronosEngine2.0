bl_info = {
    "name": "Chronos MCP Server",
    "author": "Chronos Engine",
    "version": (1, 1),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > Chronos",
    "description": "MCP Server for AI-driven 3D generation",
    "category": "Interface",
}

import bpy
import asyncio
import json
import traceback
import threading
from bpy.types import Panel, Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty

mcp_server = None

class MCPServer:
    def __init__(self, host='127.0.0.1', port=9876):
        self.host = host
        self.port = port
        self.loop = None
        self.thread = None
        self.server = None
        self.running = False
        self.websockets = None

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
        """Обработчик подключения клиента (для websockets 16.0)"""
        print(f"✅ Client connected")
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    print(f"📨 Received: {data.get('action')}")
                    result = await self.execute_command(data)
                    await websocket.send(json.dumps(result))
                    print(f"📤 Sent response")
                except Exception as e:
                    error_msg = {"status": "error", "message": str(e), "trace": traceback.format_exc()}
                    await websocket.send(json.dumps(error_msg))
                    print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ Client handler error: {e}")

    async def execute_command(self, cmd):
        """Выполняет команду в основном потоке Blender"""
        future = asyncio.get_event_loop().create_future()
        
        def run_in_main():
            try:
                action = cmd.get("action")
                args = cmd.get("args", {})
                
                if action == "run_python":
                    code = args.get("code", "")
                    # Выполняем код в глобальном пространстве Blender
                    exec_globals = {"bpy": bpy, "__name__": "__main__"}
                    exec(code, exec_globals)
                    result = {"status": "ok", "message": "Code executed successfully"}
                    
                elif action == "get_scene_data":
                    objects = []
                    for obj in bpy.context.scene.objects:
                        objects.append({
                            "name": obj.name,
                            "type": obj.type,
                            "location": list(obj.location),
                            "rotation": list(obj.rotation_euler),
                            "scale": list(obj.scale)
                        })
                    result = {"status": "ok", "data": {"objects": objects}}
                    
                else:
                    result = {"status": "error", "message": f"Unknown action: {action}"}
                    
            except Exception as e:
                result = {"status": "error", "message": str(e), "trace": traceback.format_exc()}
            
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
        self.server = await self.websockets.serve(
            self.handle_client, 
            self.host, 
            self.port
        )
        self.running = True
        print(f"✅ Server running on ws://{self.host}:{self.port}")
        await self.server.wait_closed()

    def _run_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.start_server())
        except Exception as e:
            print(f"❌ Server error: {e}")

    def start(self):
        if self.running:
            print("Server already running")
            return
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        if self.server and self.running:
            async def shutdown():
                self.server.close()
                await self.server.wait_closed()
                self.running = False
                print("Server stopped")
            if self.loop:
                asyncio.run_coroutine_threadsafe(shutdown(), self.loop)

# ============================================================
# UI Panel
# ============================================================
class CHRONOS_PT_MCP(Panel):
    bl_label = "Chronos MCP"
    bl_idname = "CHRONOS_PT_MCP"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Chronos"

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons[__name__].preferences
        
        layout.prop(prefs, "host")
        layout.prop(prefs, "port")
        layout.separator()
        
        global mcp_server
        if mcp_server and mcp_server.running:
            layout.label(text="Status: 🟢 RUNNING")
            layout.operator("chronos.stop_server", text="Stop Server")
        else:
            layout.label(text="Status: 🔴 STOPPED")
            layout.operator("chronos.start_server", text="Start Server")

class CHRONOS_OT_StartServer(Operator):
    bl_idname = "chronos.start_server"
    bl_label = "Start MCP Server"
    
    def execute(self, context):
        global mcp_server
        prefs = context.preferences.addons[__name__].preferences
        
        if mcp_server is None:
            mcp_server = MCPServer(host=prefs.host, port=prefs.port)
        mcp_server.start()
        self.report({'INFO'}, f"MCP Server started on {prefs.host}:{prefs.port}")
        return {'FINISHED'}

class CHRONOS_OT_StopServer(Operator):
    bl_idname = "chronos.stop_server"
    bl_label = "Stop MCP Server"
    
    def execute(self, context):
        global mcp_server
        if mcp_server:
            mcp_server.stop()
            mcp_server = None
        self.report({'INFO'}, "MCP Server stopped")
        return {'FINISHED'}

class CHRONOS_AddonPreferences(AddonPreferences):
    bl_idname = __name__
    host: StringProperty(name="Host", default="127.0.0.1")
    port: IntProperty(name="Port", default=9876, min=1024, max=65535)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "host")
        layout.prop(self, "port")

def register():
    bpy.utils.register_class(CHRONOS_AddonPreferences)
    bpy.utils.register_class(CHRONOS_PT_MCP)
    bpy.utils.register_class(CHRONOS_OT_StartServer)
    bpy.utils.register_class(CHRONOS_OT_StopServer)
    print("✅ Chronos MCP Server addon registered")

def unregister():
    global mcp_server
    if mcp_server:
        mcp_server.stop()
    bpy.utils.unregister_class(CHRONOS_AddonPreferences)
    bpy.utils.unregister_class(CHRONOS_PT_MCP)
    bpy.utils.unregister_class(CHRONOS_OT_StartServer)
    bpy.utils.unregister_class(CHRONOS_OT_StopServer)
    print("Chronos MCP Server addon unregistered")

if __name__ == "__main__":
    register()