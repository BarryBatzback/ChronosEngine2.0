# test_geometry_agent_rag.py
from services.blender_knowledge_base import BlenderKnowledgeBase
from services.llm_service import LLMService
from services.blender_service import BlenderService

# Инициализируем сервисы
kb = BlenderKnowledgeBase()
llm = LLMService({})
blender = BlenderService({})

# Тест получения контекста
user_prompt = "create a fantasy sword with detailed blade"
context = kb.get_context_for_llm(user_prompt)

print("📚 Context from knowledge base:")
print(context[:500] + "..." if len(context) > 500 else context)
print(f"\nContext length: {len(context)} characters")
