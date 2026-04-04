# check_asset_paths.py
from pathlib import Path

def check_asset_paths():
    """Проверяет существование ассетов"""
    assets_dir = Path("assets")
    
    print("🔍 Checking asset paths...")
    print(f"Assets directory: {assets_dir.absolute()}")
    print(f"Exists: {assets_dir.exists()}")
    
    if assets_dir.exists():
        print("\n📁 Contents:")
        for category in ["blades", "handles", "guards"]:
            category_dir = assets_dir / category
            print(f"  {category}/: {category_dir.exists()}")
            
            if category_dir.exists():
                for file in category_dir.glob("*.blend"):
                    print(f"    📄 {file.name}: {file.exists()} ({file.stat().st_size} bytes)")
                    
                    # Проверяем можно ли прочитать
                    try:
                        with open(file, 'rb') as f:
                            header = f.read(10)
                            print(f"      Header: {header[:7]}...")
                    except Exception as e:
                        print(f"      ❌ Read error: {e}")

if __name__ == "__main__":
    check_asset_paths()
