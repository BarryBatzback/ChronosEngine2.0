"""
Инструмент для извлечения данных из документации Blender 5.1
Сохраняет API в формате JSON для использования в оркестраторе
"""

import os
import json
import re
from bs4 import BeautifulSoup
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class BlenderDocExtractor:
    """Извлекает информацию из HTML-документации Blender"""
    
    def __init__(self, docs_dir: str):
        """
        Инициализация извлекателя
        
        Args:
            docs_dir: Путь к папке с HTML-документацией Blender
        """
        self.docs_dir = docs_dir
        self.api_data = {
            "modules": {},
            "deprecated": {},
            "error_patterns": {}
        }
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Настройка шаблонов для обнаружения ошибок"""
        self.api_data["error_patterns"] = {
            "attribute_error": {
                "pattern": r"AttributeError: '(\w+)' object has no attribute '(\w+)'",
                "fix": "В Blender 5.1 объект {0} не имеет атрибута {1}. Используйте актуальный API."
            },
            "keyword_error": {
                "pattern": r"Converting py args to operator properties:: keyword \"(\w+)\" unrecognized",
                "fix": "Оператор не принимает параметр '{0}'. В Blender 5.1 используйте другие параметры."
            },
            "texture_error": {
                "pattern": r"'(\w+Texture)' object has no attribute 'image'",
                "fix": "В Blender 5.1 текстуры управляются через узлы материалов, а не через bpy.data.textures."
            }
        }
    
    def extract(self, output_path: str = "blender_5_1_api.json"):
        """
        Извлекает данные из документации и сохраняет в JSON
        
        Args:
            output_path: Путь для сохранения JSON-файла
        """
        logging.info(f"Начало извлечения документации из {self.docs_dir}")
        
        # Обработка всех HTML-файлов
        html_files = list(Path(self.docs_dir).rglob("*.html"))
        total_files = len(html_files)
        
        for i, html_path in enumerate(html_files):
            rel_path = os.path.relpath(html_path, self.docs_dir)
            logging.info(f"[{i+1}/{total_files}] Обработка: {rel_path}")
            
            try:
                self._process_file(html_path)
            except Exception as e:
                logging.error(f"Ошибка при обработке {rel_path}: {str(e)}")
        
        # Сохранение результата
        self._save_api_data(output_path)
        logging.info(f"Документация успешно извлечена и сохранена в {output_path}")
    
    def _process_file(self, file_path: str):
        """Обрабатывает один HTML-файл документации"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        # Определяем тип страницы
        if "bpy.types" in file_path:
            self._extract_type_data(soup, file_path)
        elif "bpy.ops" in file_path:
            self._extract_operator_data(soup, file_path)
        elif "bpy.data" in file_path:
            self._extract_data_api(soup, file_path)
        elif "material nodes" in str(soup.title).lower():
            self._extract_material_nodes(soup, file_path)
    
    def _extract_type_data(self, soup: BeautifulSoup, file_path: str):
        """Извлекает информацию о типах данных (bpy.types)"""
        module_name = self._get_module_name(file_path, "bpy.types")
        if not module_name:
            return
        
        # Создаем структуру модуля, если её нет
        if module_name not in self.api_data["modules"]:
            self.api_data["modules"][module_name] = {
                "classes": {},
                "description": self._get_page_description(soup)
            }
        
        # Ищем классы
        for class_section in soup.select('.api-class'):
            class_name = class_section.select_one('.sig-name').text.strip()
            if not class_name:
                continue
            
            # Извлекаем методы
            methods = {}
            for method in class_section.select('.method'):
                method_name = method.select_one('.sig-name').text.strip()
                if not method_name:
                    continue
                
                params = []
                for param in method.select('.sig-param'):
                    param_text = param.get_text().strip()
                    # Убираем типы параметров для упрощения
                    param_name = param_text.split(':')[0].strip()
                    params.append(param_name)
                
                description = ""
                desc_elem = method.select_one('.description')
                if desc_elem:
                    description = desc_elem.get_text().strip()
                
                methods[method_name] = {
                    "params": params,
                    "description": description
                }
            
            # Извлекаем атрибуты
            attributes = {}
            for attr in class_section.select('.attribute'):
                attr_name = attr.select_one('.sig-name').text.strip()
                if not attr_name:
                    continue
                
                description = ""
                desc_elem = attr.select_one('.description')
                if desc_elem:
                    description = desc_elem.get_text().strip()
                
                attributes[attr_name] = {
                    "description": description
                }
            
            # Сохраняем информацию о классе
            self.api_data["modules"][module_name]["classes"][class_name] = {
                "methods": methods,
                "attributes": attributes,
                "description": self._get_section_description(class_section)
            }
    
    def _extract_operator_data(self, soup: BeautifulSoup, file_path: str):
        """Извлекает информацию об операторах (bpy.ops)"""
        module_name = self._get_module_name(file_path, "bpy.ops")
        if not module_name:
            return
        
        # Создаем структуру модуля, если её нет
        if module_name not in self.api_data["modules"]:
            self.api_data["modules"][module_name] = {
                "operators": {},
                "description": self._get_page_description(soup)
            }
        
        # Ищем операторы
        for op_section in soup.select('.api-function'):
            op_name = op_section.select_one('.sig-name').text.strip()
            if not op_name or '.' not in op_name:
                continue
            
            # Извлекаем параметры
            params = []
            for param in op_section.select('.sig-param'):
                param_text = param.get_text().strip()
                # Убираем типы параметров для упрощения
                param_name = param_text.split('=')[0].strip()
                params.append(param_name)
            
            description = ""
            desc_elem = op_section.select_one('.description')
            if desc_elem:
                description = desc_elem.get_text().strip()
            
            # Сохраняем информацию об операторе
            self.api_data["modules"][module_name]["operators"][op_name] = {
                "params": params,
                "description": description
            }
    
    def _extract_material_nodes(self, soup: BeautifulSoup, file_path: str):
        """Извлекает информацию об узлах материалов"""
        # Создаем или обновляем раздел узлов
        if "material_nodes" not in self.api_data["modules"]:
            self.api_data["modules"]["material_nodes"] = {
                "nodes": {},
                "description": "Узлы материалов в Blender 5.1"
            }
        
        # Ищем узлы
        for node_section in soup.select('.api-class'):
            node_name = node_section.select_one('.sig-name').text.strip()
            if not node_name or not node_name.startswith('ShaderNode'):
                continue
            
            # Извлекаем входы и выходы
            inputs = {}
            for input_elem in node_section.select('.input'):
                input_name = input_elem.select_one('.sig-name').text.strip()
                input_type = ""
                type_elem = input_elem.select_one('.sig-param')
                if type_elem:
                    input_type = type_elem.get_text().strip()
                
                description = ""
                desc_elem = input_elem.select_one('.description')
                if desc_elem:
                    description = desc_elem.get_text().strip()
                
                inputs[input_name] = {
                    "type": input_type,
                    "description": description
                }
            
            outputs = {}
            for output_elem in node_section.select('.output'):
                output_name = output_elem.select_one('.sig-name').text.strip()
                output_type = ""
                type_elem = output_elem.select_one('.sig-param')
                if type_elem:
                    output_type = type_elem.get_text().strip()
                
                description = ""
                desc_elem = output_elem.select_one('.description')
                if desc_elem:
                    description = desc_elem.get_text().strip()
                
                outputs[output_name] = {
                    "type": output_type,
                    "description": description
                }
            
            # Сохраняем информацию об узле
            self.api_data["modules"]["material_nodes"]["nodes"][node_name] = {
                "inputs": inputs,
                "outputs": outputs,
                "description": self._get_section_description(node_section)
            }
    
    def _get_module_name(self, file_path: str, prefix: str) -> str:
        """Определяет имя модуля из пути к файлу"""
        rel_path = os.path.relpath(file_path, self.docs_dir)
        if prefix in rel_path:
            # Удаляем префикс и расширение
            module_path = rel_path.split(prefix)[1].replace('.html', '')
            # Заменяем слеши на точки
            return module_path.replace(os.sep, '.').lstrip('.')
        return ""
    
    def _get_page_description(self, soup: BeautifulSoup) -> str:
        """Извлекает описание страницы"""
        desc_elem = soup.select_one('.description')
        if desc_elem:
            return desc_elem.get_text().strip()
        return ""
    
    def _get_section_description(self, section: BeautifulSoup) -> str:
        """Извлекает описание секции"""
        desc_elem = section.select_one('.description')
        if desc_elem:
            return desc_elem.get_text().strip()
        return ""
    
    def _save_api_data(self, output_path: str):
        """Сохраняет собранные данные в JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.api_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # Путь к вашей локальной документации Blender 5.1
    DOCS_DIR = r"C:\Program Files\Blender Foundation\Blender 5.1\5.1\datafiles\manuales\html"  # ЗАМЕНИТЕ НА ВАШ ПУТЬ
    
    # Путь для сохранения JSON
    OUTPUT_PATH = "config/blender_5_1_api.json"
    
    # Создаем папку config, если её нет
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    extractor = BlenderDocExtractor(DOCS_DIR)
    extractor.extract(OUTPUT_PATH)