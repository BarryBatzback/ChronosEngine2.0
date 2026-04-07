import ast
import logging
from typing import Dict, Any


class BlenderAPIHelper:
    """
    РРЅС‚РµР»Р»РµРєС‚СѓР°Р»СЊРЅС‹Р№ РјРѕСЃС‚ РјРµР¶РґСѓ LLM Рё Blender API.
    РћС‡РёС‰Р°РµС‚, РІР°Р»РёРґРёСЂСѓРµС‚ Рё РїРѕРґРіРѕС‚Р°РІР»РёРІР°РµС‚ РєРѕРґ Рє РёСЃРїРѕР»РЅРµРЅРёСЋ.
    Р’РµСЂСЃРёСЏ: 2.4 (Hotfix: Removal of missing_elements)
    """

    def __init__(self):
        self.logger = logging.getLogger("ChronosHelper")
        # Р—Р°РїСЂРµС‰РµРЅРЅС‹Рµ РїР°С‚С‚РµСЂРЅС‹, РєРѕС‚РѕСЂС‹Рµ С‡Р°СЃС‚Рѕ РіР°Р»Р»СЋС†РёРЅРёСЂСѓСЋС‚ РјРѕРґРµР»Рё
        self.BANNED_PATTERNS = {
            "plt.": "РСЃРїРѕР»СЊР·СѓР№ С‚РѕР»СЊРєРѕ bpy РґР»СЏ РІРёР·СѓР°Р»РёР·Р°С†РёРё, Р° РЅРµ matplotlib.",
            "input(": "РРЅС‚РµСЂР°РєС‚РёРІРЅС‹Р№ РІРІРѕРґ Р·Р°Р±Р»РѕРєРёСЂРѕРІР°РЅ РІ headless-СЂРµР¶РёРјРµ.",
            "os.exit": "РќРµР»СЊР·СЏ Р·Р°РєСЂС‹РІР°С‚СЊ РїСЂРѕС†РµСЃСЃ Blender РёР·РЅСѓС‚СЂРё СЃРєСЂРёРїС‚Р°.",
            "cv2": "OpenCV РЅРµ СѓСЃС‚Р°РЅРѕРІР»РµРЅ РІ СЃС‚Р°РЅРґР°СЂС‚РЅРѕРј Python Blender.",
        }

    def get_gold_standard_template(self) -> str:
        """
        Р’РѕР·РІСЂР°С‰Р°РµС‚ СЌС‚Р°Р»РѕРЅРЅС‹Р№ С€Р°Р±Р»РѕРЅ РєРѕРґР°.
        Р­С‚РѕС‚ С‚РµРєСЃС‚ РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ С‡Р°СЃС‚СЊСЋ СЃРёСЃС‚РµРјРЅРѕРіРѕ РїСЂРѕРјРїС‚Р° РґР»СЏ LLM.
        """
        return """
# --- CHRONOS TEMPLATE START ---
import bpy
import bmesh
import math
from mathutils import Vector, Matrix

def create_geometry(bm):
    # РўР’РћР™ РљРћР” Р—Р”Р•РЎР¬. РСЃРїРѕР»СЊР·СѓР№ bmesh РѕРїРµСЂР°С†РёРё.
    # РџСЂРёРјРµСЂ: bmesh.ops.create_cube(bm, size=1.0)
    pass

# --- CHRONOS TEMPLATE END ---
        """

    def _extract_pure_code(self, raw_response: str) -> str:
        """
        РР·РІР»РµРєР°РµС‚ РѕСЃРЅРѕРІРЅРѕР№ Р±Р»РѕРє РєРѕРґР° Python РёР· РѕС‚РІРµС‚Р° LLM Рё РѕС‡РёС‰Р°РµС‚ РµРіРѕ
        РѕС‚ РґСѓР±Р»РёСЂСѓСЋС‰РёС… РёРјРїРѕСЂС‚РѕРІ Рё СЃРёСЃС‚РµРјРЅРѕРіРѕ РјСѓСЃРѕСЂР°.

        Args:
            raw_response: РЎС‹СЂРѕР№ РѕС‚РІРµС‚ РѕС‚ СЏР·С‹РєРѕРІРѕР№ РјРѕРґРµР»Рё

        Returns:
            РћС‡РёС‰РµРЅРЅС‹Р№ Python-РєРѕРґ РґР»СЏ РІС‹РїРѕР»РЅРµРЅРёСЏ
        """
        import re

        # РЎРїРёСЃРѕРє РёРјРїРѕСЂС‚РѕРІ, РєРѕС‚РѕСЂС‹Рµ СѓР¶Рµ РµСЃС‚СЊ РІ wrap_in_chronos_context
        # Рё РєРѕС‚РѕСЂС‹Рµ РЅРµ РґРѕР»Р¶РЅС‹ РґСѓР±Р»РёСЂРѕРІР°С‚СЊСЃСЏ РІ С‚РµР»Рµ РєРѕРґР°
        duplicate_imports = [
            r"^import\s+bpy\s*$",
            r"^import\s+bmesh\s*$",
            r"^from\s+bpy\s+import\s+.*$",
            r"^from\s+math\s+import\s+.*$",
            r"^import\s+math\s*$",
            r"^import\s+random\s*$",
        ]

        # 1. РџРѕРёСЃРє Р±Р»РѕРєРѕРІ РєРѕРґР° РІ markdown: ```python, ```py, РёР»Рё РїСЂРѕСЃС‚Рѕ ```
        # re.DOTALL РїРѕР·РІРѕР»СЏРµС‚ .*? Р·Р°С…РІР°С‚С‹РІР°С‚СЊ РїРµСЂРµРЅРѕСЃС‹ СЃС‚СЂРѕРє
        pattern = r"```(?:python|py)?\s*\n(.*?)```"
        matches = re.findall(pattern, raw_response, re.DOTALL | re.IGNORECASE)

        if matches:
            # Р‘РµСЂС‘Рј СЃР°РјС‹Р№ РґР»РёРЅРЅС‹Р№ Р±Р»РѕРє РєРѕРґР° (РјР°Р¶РѕСЂРёС‚Р°СЂРЅС‹Р№ РІС‹Р±РѕСЂ)
            code = max(matches, key=len).strip()
        else:
            # Fallback: РµСЃР»Рё РЅРµС‚ РјР°СЂРєРґР°СѓРЅ-Р±Р»РѕРєРѕРІ, РёС‰РµРј РєРѕРґ РїРѕ РЅР°Р»РёС‡РёСЋ РёРјРїРѕСЂС‚РѕРІ
            lines = raw_response.split("\n")
            code_lines = []
            in_code = False
            for line in lines:
                stripped = line.strip()
                # РќР°С‡РёРЅР°РµРј СЃРѕР±РёСЂР°С‚СЊ РєРѕРґ, РµСЃР»Рё РІРёРґРёРј С‚РёРїРёС‡РЅСѓСЋ Python-РєРѕРЅСЃС‚СЂСѓРєС†РёСЋ
                if (
                    stripped.startswith("import ")
                    or stripped.startswith("from ")
                    or stripped.startswith("def ")
                    or stripped.startswith("class ")
                ):
                    in_code = True
                if (
                    in_code
                    and stripped
                    and not stripped.startswith("#")
                    and "```" not in stripped
                ):
                    code_lines.append(line)
            code = "\n".join(code_lines).strip() if code_lines else raw_response.strip()

        # 2. РЈРґР°Р»СЏРµРј РґСѓР±Р»РёСЂСѓСЋС‰РёРµ РёРјРїРѕСЂС‚С‹, РєРѕС‚РѕСЂС‹Рµ СѓР¶Рµ РµСЃС‚СЊ РІ РєРѕРЅС‚РµРєСЃС‚Рµ Chronos
        code_lines = code.split("\n")
        filtered_lines = []
        for line in code_lines:
            stripped = line.strip()
            # РџСЂРѕРїСѓСЃРєР°РµРј СЃС‚СЂРѕРєРё, РєРѕС‚РѕСЂС‹Рµ СЃРѕРІРїР°РґР°СЋС‚ СЃ РЅР°С€РёРјРё "Р·Р°РїСЂРµС‰С‘РЅРЅС‹РјРё" РёРјРїРѕСЂС‚Р°РјРё
            if any(re.match(pattern, stripped) for pattern in duplicate_imports):
                continue
            filtered_lines.append(line)

        code = "\n".join(filtered_lines)

        # 3. РЈРґР°Р»СЏРµРј Р»РёС€РЅРёРµ РїСѓСЃС‚С‹Рµ СЃС‚СЂРѕРєРё РІ РЅР°С‡Р°Р»Рµ Рё РєРѕРЅС†Рµ
        return code.strip()

    def fix_escape_sequences(self, code: str) -> str:
        """
        РСЃРїСЂР°РІР»СЏРµС‚ РѕС€РёР±РєСѓ W605 (invalid escape sequence).
        Р—Р°РјРµРЅСЏРµС‚ РѕРґРёРЅРѕС‡РЅС‹Рµ РѕР±СЂР°С‚РЅС‹Рµ СЃР»РµС€Рё РІ СЃС‚СЂРѕРєР°С… РЅР° РґРІРѕР№РЅС‹Рµ, РµСЃР»Рё СЌС‚Рѕ РЅРµ СЃРїРµС†СЃРёРјРІРѕР»С‹.
        """
        # РС‰РµРј РїСѓС‚Рё РёР»Рё СЃРїРµС†-СЃРёРјРІРѕР»С‹ РІ РєР°РІС‹С‡РєР°С…, РєРѕС‚РѕСЂС‹Рµ РЅРµ СЌРєСЂР°РЅРёСЂРѕРІР°РЅС‹
        return code.replace("\\", "\\\\").replace("\\\\\\\\", "\\\\")

    def validate_and_fix_syntax(self, raw_code: str) -> Dict[str, Any]:
        """
        РџСЂРѕРІРµСЂСЏРµС‚ РєРѕРґ РЅР° РЅР°Р»РёС‡РёРµ СЃРёРЅС‚Р°РєСЃРёС‡РµСЃРєРёС… РѕС€РёР±РѕРє РїРµСЂРµРґ Р·Р°РїСѓСЃРєРѕРј.
        """
        report = {"is_valid": True, "errors": [], "cleaned_code": ""}

        # РЎРЅР°С‡Р°Р»Р° РѕС‡РёС‰Р°РµРј
        code = self._extract_pure_code(raw_code)
        # РСЃРїСЂР°РІР»СЏРµРј СЃР»РµС€Рё РґР»СЏ Windows-РїСѓС‚РµР№
        code = self.fix_escape_sequences(code)

        try:
            ast.parse(code)
            report["cleaned_code"] = code
        except SyntaxError as e:
            report["is_valid"] = False
            report["errors"].append(f"Line {e.lineno}: {e.msg}")

        return report

    def wrap_in_chronos_context(
        self, logic_code: str, asset_id: str = "GEN_ASSET"
    ) -> str:
        """РћР±РѕСЂР°С‡РёРІР°РµС‚ Р»РѕРіРёРєСѓ РІ Р±РµР·РѕРїР°СЃРЅСѓСЋ С„СѓРЅРєС†РёСЋ СЃ РёРЅРёС†РёР°Р»РёР·Р°С†РёРµР№ bmesh."""
        # РџРѕРґРіРѕС‚РѕРІРєР° РѕС‚СЃС‚СѓРїРѕРІ (8 РїСЂРѕР±РµР»РѕРІ)
        indented_logic = "\n".join(
            [
                f"        {line}" if line.strip() else ""
                for line in logic_code.strip().split("\n")
            ]
        )

        return f"""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

def execute_chronos_generation():
    print("рџ›  Chronos: Start generation of {asset_id}")

    # РћС‡РёСЃС‚РєР° СЃС‚Р°СЂРѕРіРѕ РѕР±СЉРµРєС‚Р°
    if "{asset_id}" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["{asset_id}"], do_unlink=True)

    mesh_data = bpy.data.meshes.new("{asset_id}_mesh")
    obj = bpy.data.objects.new("{asset_id}", mesh_data)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()

    try:
{indented_logic}

        # Р¤РёРЅР°Р»РёР·Р°С†РёСЏ
        bm.to_mesh(mesh_data)
        bm.free()
        bpy.context.view_layer.update()
        print("вњ… Chronos: {asset_id} successfully created.")

    except Exception as e:
        if bm: bm.free()
        print(f"вќЊ Execution Error: {{str(e)}}")
        raise e

if __name__ == "__main__":
    execute_chronos_generation()
"""

    def get_api_hint(self, context: str) -> str:
        """РџРѕРґСЃРєР°Р·РєРё РґР»СЏ СЃРёСЃС‚РµРјРЅРѕРіРѕ РїСЂРѕРјРїС‚Р°."""
        hints = {
            "prop": "Use bmesh.ops.create_cube for basic shapes. Ensure you use bm.verts.ensure_lookup_table() before accessing indices.",
            "weapon": "Focus on thin extruded bmesh regions for blades.",
            "architecture": "Use nested loops for repeating elements like steps or windows.",
        }
        return hints.get(context, "Use bmesh API for geometry generation.")
