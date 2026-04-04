# test_search_after_init.py
from services.blender_knowledge_base import BlenderKnowledgeBase

kb = BlenderKnowledgeBase()

# Тестовые запросы
test_queries = [
    "create mesh from vertices",
    "bpy.ops.mesh.primitive_cube_add", 
    "material nodes shader",
    "object transformation",
    "blender geometry"
]

for query in test_queries:
    print(f"\n🔍 Searching for: '{query}'")
    results = kb.search(query, n_results=2)
    print(f"Found {len(results)} results")
    
    for i, result in enumerate(results):
        print(f"  {i+1}. {result['name']}")
        print(f"     Type: {result['type']}")
        if result['signature']:
            print(f"     Signature: {result['signature'][:100]}...")
        print(f"     Content: {result['content'][:150]}...")
        print()
