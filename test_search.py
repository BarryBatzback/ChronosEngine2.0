# test_search.py
from services.blender_knowledge_base import BlenderKnowledgeBase

def test_knowledge_base():
    kb = BlenderKnowledgeBase()
    
    print("🧪 Testing Blender Knowledge Base Search")
    print("=" * 50)
    
    # Тестовые запросы для различных сценариев
    test_cases = [
        ("create mesh from vertices", "Генерация меша"),
        ("bpy.ops.mesh.primitive_cube_add", "Создание куба"),
        ("material shader nodes", "Материалы и ноды"),
        ("object transformation location", "Трансформация объектов"),
        ("blender bmesh create", "BMesh создание"),
        ("curve extrusion", "Экструзия кривых"),
        ("modifier bevel", "Модификатор скоса"),
        ("texture mapping", "Текстурирование")
    ]
    
    for query, description in test_cases:
        print(f"\n🔍 {description}: '{query}'")
        results = kb.search(query, n_results=3)
        
        print(f"   Found {len(results)} results")
        for i, result in enumerate(results):
            print(f"   {i+1}. {result['name']} ({result['type']})")
            if result.get('signature'):
                print(f"      Sig: {result['signature'][:80]}...")
            print(f"      Content: {result['content'][:100]}...")
            print()

if __name__ == "__main__":
    test_knowledge_base()
