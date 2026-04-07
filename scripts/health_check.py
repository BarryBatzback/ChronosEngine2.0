#!/usr/bin/env python
"""
Проверка здоровья системы
"""

import sys
import socket
from pathlib import Path


def check_python():
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    print(f"❌ Python {version.major}.{version.minor} - need 3.10+")
    return False


def check_dependencies():
    required = ["ollama", "pyyaml", "pydantic", "sqlalchemy", "loguru"]
    missing = []

    for dep in required:
        try:
            __import__(dep.replace(".", "_"))
        except ImportError:
            missing.append(dep)

    if not missing:
        print("✅ All dependencies installed")
        return True
    print(f"❌ Missing: {', '.join(missing)}")
    return False


def check_blender_mcp(host="localhost", port=9876):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    if result == 0:
        print(f"✅ Blender MCP server running on {host}:{port}")
        return True
    print(f"⚠️ Blender MCP server not running (start Blender with addon)")
    return True  # Не блокируем, это можно запустить позже


def check_comfyui(host="localhost", port=8188):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    if result == 0:
        print(f"✅ ComfyUI running on {host}:{port}")
        return True
    print(f"⚠️ ComfyUI not running (start ComfyUI first)")
    return True  # Не блокируем


def check_ollama():
    """Проверка Ollama и моделей Qwen"""
    try:
        import ollama

        client = ollama.Client(host="http://localhost:11434")

        # Проверка подключения
        models = client.list()
        print(f"✅ Ollama running (found {len(models.get('models', []))} models)")

        # Проверка конкретных моделей
        model_names = [m["name"] for m in models.get("models", [])]

        required = ["qwen2.5:14b", "qwen2.5:7b"]
        missing = [m for m in required if not any(m in name for name in model_names)]

        if missing:
            print(f"⚠️ Missing models: {', '.join(missing)}")
            print("   Run: python scripts/setup_qwen.ps1")
            return False
        else:
            print("✅ All required Qwen models available")
            return True

    except Exception as e:
        print(f"❌ Ollama not running: {e}")
        print("   Install: https://ollama.com")
        print("   Run: ollama serve")
        return False


def check_directories():
    required = ["config", "logs", "output", "database", "workflows"]
    missing = []

    for dir in required:
        if not Path(dir).exists():
            missing.append(dir)

    if not missing:
        print("✅ All directories exist")
        return True
    print(f"❌ Missing directories: {', '.join(missing)}")
    return False


def main():
    print("\n" + "=" * 50)
    print("  GAME ASSET ORCHESTRATOR - HEALTH CHECK")
    print("=" * 50 + "\n")

    checks = [
        ("Python", check_python),
        ("Dependencies", check_dependencies),
        ("Directories", check_directories),
        ("Ollama + Qwen", check_ollama),
        ("Blender MCP", check_blender_mcp),
        ("ComfyUI", check_comfyui),
    ]

    passed = 0
    for name, check_func in checks:
        print(f"{name}: ", end="")
        if check_func():
            passed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{len(checks)} checks passed")

    if passed == len(checks):
        print("✅ System ready! Run: python main.py")
    else:
        print("⚠️ Fix failing checks before proceeding")

    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
