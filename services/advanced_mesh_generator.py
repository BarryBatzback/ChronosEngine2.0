from typing import List, Dict
from .blender_api_helper import BlenderAPIHelper

class AdvancedMeshGenerator:
    def __init__(self):
        self.api_helper = BlenderAPIHelper()

    def generate_component_code(self, component_type: str, params: Dict) -> str:
        """
        Генерирует чистый BMesh код.
        Никаких bpy.ops. Все операции через индексы и вершины.
        """
        # Базовая логика для меча (лезвие)
        if component_type == "blade":
            length = params.get("length", 1.0)
            width = params.get("width", 0.1)
            
            # Мы даем модели этот шаблон как "золотой стандарт"
            logic = f"""
# Параметры: длина={length}, ширина={width}
verts = [
    bm.verts.new((- {width}/2, 0, 0)),
    bm.verts.new(({width}/2, 0, 0)),
    bm.verts.new(({width}/2, 0.01, {length})),
    bm.verts.new((- {width}/2, 0.01, {length})),
    bm.verts.new((0, 0, {length} * 1.1)) # Острие
]

# Создание граней
bm.faces.new(verts[0:4]) # Основное тело
bm.faces.new([verts[2], verts[3], verts[4]]) # Кончик
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
"""
            return self.api_helper.wrap_in_boilerplate(logic)
        
        return ""