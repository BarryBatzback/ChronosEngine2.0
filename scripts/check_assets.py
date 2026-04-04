# scripts/check_assets.py
from pathlib import Path

def check_assets():
    assets_dir = Path("assets")
    print("🔍 Checking assets directory...")
    print(f"Assets path: {assets_dir.absolute()}")
    print(f"Exists: {assets_dir.exists()}")
    
    if assets_dir.exists():
        print("\n📁 Contents:")
        for item in assets_dir.iterdir():
            if item.is_dir():
                print(f"  📂 {item.name}/")
                for subitem in item.iterdir():
                    print(f"    📄 {subitem.name}")
            else:
                print(f"  📄 {item.name}")
    
    # Проверка конкретных файлов
    required_files = [
        assets_dir / "blades" / "basic_blade.blend",
        assets_dir / "handles" / "basic_handle.blend", 
        assets_dir / "guards" / "basic_guard.blend"
    ]
    
    print("\n✅ Required files check:")
    for file in required_files:
        print(f"  {file.name}: {'FOUND' if file.exists() else 'MISSING'}")

if __name__ == "__main__":
    check_assets()
