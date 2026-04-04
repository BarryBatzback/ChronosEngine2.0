# debug_code_sender.py
from services.blender_service import BlenderService

async def debug_code():
    blender = BlenderService({})
    
    if await blender.connect():
        # Получаем код который сейчас генерируется
        from services.component_library import ComponentLibrary
        lib = ComponentLibrary()
        
        code = lib.import_component_code('sword', 'blade', 'basic', [0, 0, 0])
        
        print("🔍 Generated code:")
        print("=" * 50)
        for i, line in enumerate(code.split('\n')[:10], 1):  # Первые 10 строк
            print(f"{i:2d}: {repr(line)}")
        print("=" * 50)
        
        # Проверяем отступы
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if line.startswith(' ') and not line.startswith('    '):
                print(f"⚠️ Suspicious indent line {i}: {repr(line)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(debug_code())
