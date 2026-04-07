import json
import re
from loguru import logger


class GeometryAgent:
    def __init__(self, llm_service, blender_service, knowledge_base):
        self.llm = llm_service
        self.blender = blender_service
        self.kb = knowledge_base

    async def execute(self, task: dict, session_id: str):
        prompt = task.get("prompt", "primitive")
        code = ""  # Инициализируем пустой строкой на случай ошибки в _analyze_structure

        try:
            # 1. Запрос структуры
            structure = await self._analyze_structure(prompt)

            # 2. Генерация кода
            code = self._build_procedural_code(structure)

            # 🔥 ВАЖНО: логируем код ЗДЕСЬ, перед отправкой
            logger.debug(f"SENDING CODE TO BLENDER:\n{code}")

            # 3. Отправка в Blender
            result = await self.blender.run_python(code)

            if result and result.get("status") == "success":
                return {
                    "success": True,
                    "message": f'Asset "{structure.get("name", "unknown")}" generated',
                    "code": code,
                }

            return {"success": False, "message": result.get("message", "Blender Error")}

        except Exception as e:
            # Если упало на этапе генерации кода или анализа
            logger.error(f"Agent Error: {e}")
            # Если код успел сгенерироваться частично, полезно его увидеть в логе ошибки
            if code:
                logger.debug(f"Failed code attempt:\n{code}")
            return {"success": False, "message": str(e)}

    async def _analyze_structure(self, prompt: str):
        system_prompt = """
        Ты — мастер-ремесленник. Разбей объект на простые блоки (CUBE, CYLINDER).
        Выдай ТОЛЬКО JSON:
        {
            "name": "string",
            "elements": [
                {
                    "part": "название",
                    "shape": "CUBE" или "CYLINDER",
                    "size": [width, depth, height], 
                    "layer": 0 (0-база, 1-выше и т.д.),
                    "color": [r, g, b]
                }
            ]
        }
        Важно: размеры в метрах. Лезвие меча ~1.2м, рукоять ~0.2м.
        """
        response = await self.llm.generate(f"{system_prompt}\nЗапрос: {prompt}")
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        return json.loads(json_match.group())

    def _build_procedural_code(self, structure: dict) -> str:
        elements = sorted(
            structure.get("elements", []), key=lambda x: x.get("layer", 0)
        )

        gen_lines = []
        # Логика автоматической укладки по вертикали
        gen_lines.append("        current_z = 0.0")

        for el in elements:
            shape = el.get("shape", "CUBE").lower()
            w, d, h = el["size"]
            color = el.get("color", [0.5, 0.5, 0.5])

            # В Blender для примитивов:
            # cube_add использует 'size' (радиус), cylinder_add использует 'radius' и 'depth'
            if shape == "cylinder":
                add_cmd = f"bpy.ops.mesh.primitive_cylinder_add(radius={w/2}, depth={h}, location=(0, 0, current_z + {h/2}))"
            else:
                add_cmd = f"bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, current_z + {h/2}))"

            gen_lines.append(f"""
        # --- Часть: {el['part']} ---
        {add_cmd}
        obj = bpy.context.active_object
        obj.name = "{el['part']}"
        obj.dimensions = ({w}, {d}, {h})
        
        # Материал
        mat = bpy.data.materials.new(name="Mat_{el['part']}")
        mat.use_nodes = True
        mat.node_tree.nodes['Principled BSDF'].inputs[0].default_value = ({color[0]}, {color[1]}, {color[2]}, 1.0)
        obj.data.materials.append(mat)
        
        current_z += {h}  # Поднимаем уровень для следующей детали
            """)

        body = "\n".join(gen_lines)
        return f"""
import bpy
import json

def construct():
    try:
        if bpy.ops.object.select_all.poll():
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()
{body}
        return {{"status": "success"}}
    except Exception as e:
        return {{"status": "error", "message": str(e)}}

print(json.dumps(construct()))
        """.strip()
