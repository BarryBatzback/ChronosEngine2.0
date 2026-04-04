# test_simple_component.py
from services.component_library import ComponentLibrary

def test_simple_component():
    lib = ComponentLibrary()
    
    # Тестируем генерацию кода
    code = lib.import_component_code('sword', 'blade', 'basic', [0, 0, 0])
    
    print("🔍 Generated code:")
    print("=" * 50)
    print(code)
    print("=" * 50)
    
    # Проверяем на синтаксические ошибки
    try:
        compile(code, '<string>', 'exec')
        print("✅ Code compiles successfully")
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        print(f"Error at line {e.lineno}: {e.text}")

if __name__ == "__main__":
    test_simple_component()
