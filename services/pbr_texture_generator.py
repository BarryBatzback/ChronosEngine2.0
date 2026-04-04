"""
Генерация PBR текстур через узлы Blender
"""

from typing import Dict, Any
from loguru import logger


class PBRTextureGenerator:
    def __init__(self, llm_service):
        self.llm = llm_service

    def create_wood_material(self, name: str = "Wood") -> str:
        return '''
def create_wood_material():
    mat = bpy.data.materials.new("Wood")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    principled.inputs['Roughness'].default_value = 0.6
    
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-200, 100)
    noise.inputs['Scale'].default_value = 5.0
    
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (0, 100)
    color_ramp.color_ramp.elements[0].color = (0.35, 0.22, 0.12, 1.0)
    color_ramp.color_ramp.elements[1].color = (0.55, 0.38, 0.22, 1.0)
    
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

wood_mat = create_wood_material()
print("✅ Wood material created")
'''

    def create_metal_material(self, name: str = "Metal") -> str:
        return '''
def create_metal_material():
    mat = bpy.data.materials.new("Metal")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    principled.inputs['Metallic'].default_value = 1.0
    principled.inputs['Roughness'].default_value = 0.3
    principled.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

metal_mat = create_metal_material()
print("✅ Metal material created")
'''