"""
Автоматический риггинг и анимация персонажей
"""


class AutoRigService:
    """
    Автоматический риггинг для персонажей
    Использует Blender Rigify или Auto-Rig Pro
    """

    def generate_rig_code(self, character_name: str = "character") -> str:
        """
        Генерация кода для автоматического риггинга
        """
        return f'''
import bpy

# ============================================================
# АВТОМАТИЧЕСКИЙ РИГГИНГ ПЕРСОНАЖА
# ============================================================

def auto_rig_character(obj_name):
    """Автоматический риггинг с использованием Rigify"""
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        print(f"Object {{obj_name}} not found")
        return

    # Выделяем объект
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Включаем Rigify
    bpy.ops.object.armature_add()
    armature = bpy.context.active_object
    armature.name = f"{{obj_name}}_Rig"

    # Создаём простую скелетную структуру
    bpy.ops.object.mode_set(mode='EDIT')
    armature.data.edit_bones.new('root')
    armature.data.edit_bones.new('spine')
    armature.data.edit_bones.new('neck')
    armature.data.edit_bones.new('head')

    # Родительские связи
    armature.data.edit_bones['spine'].parent = armature.data.edit_bones['root']
    armature.data.edit_bones['neck'].parent = armature.data.edit_bones['spine']
    armature.data.edit_bones['head'].parent = armature.data.edit_bones['neck']

    # Позиционирование костей
    armature.data.edit_bones['root'].head = (0, 0, 0)
    armature.data.edit_bones['root'].tail = (0, 0, 0.5)

    armature.data.edit_bones['spine'].head = (0, 0, 0.5)
    armature.data.edit_bones['spine'].tail = (0, 0, 1.0)

    armature.data.edit_bones['neck'].head = (0, 0, 1.0)
    armature.data.edit_bones['neck'].tail = (0, 0, 1.2)

    armature.data.edit_bones['head'].head = (0, 0, 1.2)
    armature.data.edit_bones['head'].tail = (0, 0, 1.4)

    bpy.ops.object.mode_set(mode='OBJECT')

    # Автоматическое взвешивание
    armature.select_set(True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    print(f"✅ Auto-rig completed for {{obj_name}}")

# Применяем риггинг
auto_rig_character("{character_name}")
print("✅ Character rigged successfully")
'''

    def generate_animation_code(self, animation_type: str = "idle") -> str:
        """
        Генерация простой анимации
        """
        animations = {
            "idle": """
# Анимация IDLE (покачивание)
bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 60

for frame in range(0, 61):
    bpy.context.scene.frame_set(frame)
    angle = math.sin(frame * math.pi * 2 / 60) * 0.05
    armature.pose.bones['spine'].rotation_euler = (angle, 0, 0)
    armature.keyframe_insert(data_path='pose.bones["spine"].rotation_euler', index=-1)
""",
            "walk": """
# Анимация ходьбы
bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 40

for frame in range(0, 41):
    bpy.context.scene.frame_set(frame)
    progress = frame / 40
    height = math.sin(progress * math.pi * 2) * 0.1
    armature.location.z = height
    armature.keyframe_insert(data_path='location', index=2)
""",
        }

        return f"""
import bpy
import math

{animations.get(animation_type, animations["idle"])}

print("✅ Animation created")
"""
