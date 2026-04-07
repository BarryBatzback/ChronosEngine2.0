# import os
# import requests
# from loguru import logger
# from pathlib import Path

# class AssetFetcher:
# def __init__(self, assets_dir: str = "assets"):
# self.assets_dir = Path(assets_dir)
# self.api_url = "https://api.poly.pizza/v1/search/"
# Создаем папки если их нет
# self.assets_dir.mkdir(exist_ok=True)

# def fetch_model(self, keyword: str, category: str) -> str:
# """Поиск и скачивание модели. Возвращает путь к файлу."""
# target_dir = self.assets_dir / category
# target_dir.mkdir(exist_ok=True)
# file_path = target_dir / f"{keyword}.glb"

# Если файл уже есть, не качаем заново
# if file_path.exists():
# return str(file_path).replace("\\", "/")

# logger.info(f"🌐 Searching online for: {keyword}")
# try:
# Поиск через публичный эндпоинт Poly.pizza
# response = requests.get(f"{self.api_url}{keyword}", timeout=10)
# if response.status_code == 200:
# results = response.json().get('results', [])
# if not results:
# logger.warning(f"❓ No models found for '{keyword}'")
# return ""

# Берем первый результат (самый релевантный)
# model_url = results[0].get('DownloadUrl')
# if model_url:
#   logger.info(f"📥 Downloading {keyword} from Poly.pizza...")
#  model_data = requests.get(model_url).content
# with open(file_path, "wb") as f:
#    f.write(model_data)
# return str(file_path).replace("\\", "/")
# except Exception as e:
#   logger.error(f"❌ Failed to fetch asset: {e}")

# return ""
