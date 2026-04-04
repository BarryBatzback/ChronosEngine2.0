"""
Помощник для работы с документацией Blender API
Поддерживает как компактный JSON, так и полную HTML документацию
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


class BlenderAPIHelper:
    """Справочник Blender API с поиском по документации"""
    
    def __init__(self, use_vector_db: bool = True, docs_path: str = None):
        self.use_vector_db = use_vector_db
        self.knowledge_base = None
        
        if use_vector_db and docs_path:
            try:
                from services.blender_knowledge_base import BlenderKnowledgeBase
                self.knowledge_base = BlenderKnowledgeBase(docs_path)
                logger.info("🧠 Vector knowledge base initialized")
            except Exception as e:
                logger.warning(f"Failed to init vector DB: {e}, using fallback")
                self.use_vector_db = False
        
        if not self.use_vector_db:
            self._load_compact_reference()
    
    def _load_compact_reference(self):
        """Загрузка компактного JSON справочника (fallback)"""
        reference_path = Path("data/blender_api_reference.json")
        if reference_path.exists():
            with open(reference_path, 'r', encoding='utf-8') as f:
                self.reference = json.load(f)
        else:
            self.reference = self._create_default_reference()
    
    def _create_default_reference(self) -> Dict:
        """Создание базового справочника"""
        return {
            "mesh_creation": {
                "from_pydata": "mesh.from_pydata(vertices, [], faces)",
                "primitive_cube": "bpy.ops.mesh.primitive_cube_add(size=2)",
            },
            "materials": {
                "use_nodes": "material.use_nodes = True",
                "principled_bsdf": "Principled BSDF node for PBR materials",
            },
            "common_gotchas": {
                "update_view_layer": "bpy.context.view_layer.update()",
                "edit_mode": "bpy.ops.object.mode_set(mode='OBJECT')",
            }
        }
    
    async def get_context_for_query(self, query: str) -> str:
        """
        Получение релевантного контекста из документации
        
        Args:
            query: Запрос пользователя или описание нужной функциональности
            
        Returns:
            Строка с контекстом для LLM
        """
        if self.use_vector_db and self.knowledge_base:
            return self.knowledge_base.get_context_for_llm(query)
        else:
            return self._get_fallback_context(query)
    
    def _get_fallback_context(self, query: str) -> str:
        """Fallback контекст из компактного справочника"""
        query_lower = query.lower()
        
        if "mesh" in query_lower or "create" in query_lower:
            return f"""
# Blender API Reference (Mesh Creation)
- from_pydata: {self.reference.get('mesh_creation', {}).get('from_pydata', '')}
- primitive_cube: {self.reference.get('mesh_creation', {}).get('primitive_cube', '')}
"""
        elif "material" in query_lower or "texture" in query_lower:
            return f"""
# Blender API Reference (Materials)
- use_nodes: {self.reference.get('materials', {}).get('use_nodes', '')}
- principled_bsdf: {self.reference.get('materials', {}).get('principled_bsdf', '')}
"""
        else:
            return f"""
# Blender API Reference (General)
- update_view_layer: {self.reference.get('common_gotchas', {}).get('update_view_layer', '')}
- edit_mode: {self.reference.get('common_gotchas', {}).get('edit_mode', '')}
"""
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """Базовая валидация кода"""
        issues = []
        
        # Проверка на deprecated API
        if "bpy.data.textures" in code:
            issues.append({
                "pattern": "bpy.data.textures",
                "suggestion": "Use material nodes instead (material.use_nodes = True)",
                "severity": "warning"
            })
        
        # Проверка на вызов update
        if "bpy.ops.mesh.primitive" in code and "bpy.context.view_layer.update()" not in code:
            issues.append({
                "pattern": "missing_view_layer_update",
                "suggestion": "Add bpy.context.view_layer.update() after creating objects",
                "severity": "info"
            })
        
        return {
            "issues": issues,
            "valid": len([i for i in issues if i["severity"] == "error"]) == 0
        }