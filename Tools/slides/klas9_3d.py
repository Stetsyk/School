"""Спільне для колод 9 класу «3D-графіка» (Blender, уроки ІІ-03…ІІ-15): сцени (Python-код для Blender),
готові зразки-додатки (.blend + рендер PNG / відео) і типові слайди.

Сцена — рядок Python-коду для Blender (див. PRELUDE у blendershot.py: add, clean, ground, world, sun, mat, look…).
Той самий код будує і скрін інтерфейсу (blenderkroky.bk), і додаток (blendershot.bmake), тож зразок у «Додатках»
збігається з тим, що на слайді."""
import glob
import os

from deck import Deck, REPO, INK2, data_uri
import gdocs  # noqa: F401  — s.gshot, s.gsteps, s.gsteps_row
from blendershot import bmake

ADD_DIR = os.path.join(REPO, "Презентації уроків", "9 клас", "Додатки")
OUT_DIR = os.path.join(REPO, "Презентації уроків", "9 клас")

LESSON = {
    3: "Урок ІІ-03. Тривимірна графіка",
    4: "Урок ІІ-04. Редактор Blender. Примітиви й навігація",
    5: "Урок ІІ-05. Примітиви. Переміщення об’єктів",
    6: "Урок ІІ-06. Масштабування й обертання",
    7: "Урок ІІ-07. Просторові моделі з примітивів",
    8: "Урок ІІ-08. Складені моделі",
    9: "Урок ІІ-09. Форма, матеріали й текстури",
    10: "Урок ІІ-10. Практична робота № 6. 3D-моделі",
    11: "Урок ІІ-11. Анімаційні ефекти",
    12: "Урок ІІ-12. Анімація руху",
    13: "Урок ІІ-13. Практична робота № 7. 3D-анімація",
    14: "Урок ІІ-14. 3D-друк",
    15: "Урок ІІ-15. Підсумок розділу «3D-графіка»",
}

# ------------------------------------------------------------------ сцени
SMOOTH = '''
for _o in bpy.data.objects:
    if _o.type == "MESH" and _o.name not in ("Підлога",) and not _o.name.startswith(("Куб", "Стільниця", "Ніжка", "Сидіння", "Спинка", "Стіна", "Двері", "Вікно", "Дах", "Дошка", "Опора", "Брус", "Труба", "Основа", "Ящик")):
        bpy.context.view_layer.objects.active = _o
        bpy.ops.object.shade_smooth()
'''

PRIMS = '''
clean(cam=(10, -10, 7), target=(0, 0, 0.8))
add("cube", "Куб", loc=(-4.5, 0, 1), color="#E8772E")
add("uv_sphere", "Сфера", loc=(-1.5, 0, 1), color="#2F6FB7", segments=48, ring_count=24)
add("cylinder", "Циліндр", loc=(1.5, 0, 1), color="#4E8F4A", vertices=48)
add("cone", "Конус", loc=(4.5, 0, 1), color="#D9342B", vertices=48)
add("torus", "Тор", loc=(0, 3.5, 0.25), color="#F7CE46", major_segments=64, minor_segments=24)
''' + SMOOTH

BENCH = '''
clean(cam=(8, -8, 5.5), target=(0, 0, 0.6))
add("cube", "Сидіння", loc=(0, 0, 0.9), scale=(2, 0.5, 0.08), color="#B5793C")
add("cube", "Спинка", loc=(0, 0.45, 1.6), scale=(2, 0.06, 0.4), color="#B5793C")
for i, x in enumerate((-1.6, 1.6)):
    add("cube", "Ніжка %d" % (i + 1), loc=(x, 0, 0.42), scale=(0.08, 0.45, 0.42), color="#3A3D42")
'''

SNOWMAN = '''
clean(cam=(8, -8, 5.5), target=(0, 0, 1.7))
add("uv_sphere", "Низ", loc=(0, 0, 1.0), scale=(1, 1, 1), color="#FFFFFF", segments=48, ring_count=24)
add("uv_sphere", "Середина", loc=(0, 0, 2.45), scale=(0.7, 0.7, 0.7), color="#FFFFFF", segments=48, ring_count=24)
add("uv_sphere", "Голова", loc=(0, 0, 3.45), scale=(0.45, 0.45, 0.45), color="#FFFFFF", segments=48, ring_count=24)
add("cone", "Ніс", loc=(0.35, -0.35, 3.45), rot=(90, 0, 45), scale=(0.09, 0.09, 0.35), color="#E8772E")
add("uv_sphere", "Око ліве", loc=(0.1, -0.42, 3.62), scale=(0.06, 0.06, 0.06), color="#2F3033")
add("uv_sphere", "Око праве", loc=(0.42, -0.1, 3.62), scale=(0.06, 0.06, 0.06), color="#2F3033")
add("cylinder", "Капелюх", loc=(0, 0, 3.98), scale=(0.35, 0.35, 0.3), color="#2F3033", vertices=48)
add("cylinder", "Поля", loc=(0, 0, 3.72), scale=(0.55, 0.55, 0.03), color="#2F3033", vertices=48)
''' + SMOOTH

TREE = '''
clean(cam=(8, -8, 5.5), target=(0, 0, 1.6))
add("cylinder", "Стовбур", loc=(0, 0, 0.4), scale=(0.25, 0.25, 0.4), color="#7A5230", vertices=32)
add("cone", "Ярус 1", loc=(0, 0, 1.3), scale=(1.3, 1.3, 0.9), color="#2E7D4F", vertices=48)
add("cone", "Ярус 2", loc=(0, 0, 2.1), scale=(1.0, 1.0, 0.8), color="#2E7D4F", vertices=48)
add("cone", "Ярус 3", loc=(0, 0, 2.8), scale=(0.7, 0.7, 0.65), color="#2E7D4F", vertices=48)
add("ico_sphere", "Зірка", loc=(0, 0, 3.55), scale=(0.18, 0.18, 0.18), color="#F7CE46")
'''

TABLE = '''
clean(cam=(7, -7, 5), target=(0, 0, 0.7))
add("cube", "Стільниця", loc=(0, 0, 1.5), scale=(1.5, 1, 0.05), color="#B5793C")
for i, (x, y) in enumerate([(-1.35, -0.85), (1.35, -0.85), (-1.35, 0.85), (1.35, 0.85)]):
    add("cube", "Ніжка %d" % (i + 1), loc=(x, y, 0.725), scale=(0.07, 0.07, 0.725), color="#7A5230")
'''

CHAIR = '''
add("cube", "Сидіння", loc=(0, -2.1, 0.9), scale=(0.55, 0.55, 0.05), color="#2F6FB7")
add("cube", "Спинка", loc=(0, -2.6, 1.5), scale=(0.55, 0.05, 0.55), color="#2F6FB7")
for i, (x, y) in enumerate([(-0.48, -1.62), (0.48, -1.62), (-0.48, -2.58), (0.48, -2.58)]):
    add("cube", "Ніжка стільця %d" % (i + 1), loc=(x, y, 0.42), scale=(0.05, 0.05, 0.42), color="#3A3D42")
'''

HOUSE = '''
clean(cam=(9, -9, 6.5), target=(0, 0, 1.4))
add("cube", "Стіни", loc=(0, 0, 1), scale=(1.5, 1.2, 1), color="#C98A4B")
dah = add("cylinder", "Дах", loc=(0, 0, 2.55), rot=(90, 0, 0), scale=(1.75, 0.75, 1.3), color="#D9342B", vertices=3)
dah.rotation_euler = (math.radians(90), 0, 0)
add("cube", "Двері", loc=(0.4, -1.21, 0.6), scale=(0.3, 0.02, 0.6), color="#6E4426")
add("cube", "Вікно", loc=(-0.75, -1.21, 1.2), scale=(0.3, 0.02, 0.3), color="#8EC5F0")
add("cube", "Труба", loc=(0.8, 0.3, 2.9), scale=(0.15, 0.15, 0.4), color="#7A3B2E")
'''

ROCKET = '''
clean(cam=(9, -9, 6.5), target=(0, 0, 2))
add("cylinder", "Корпус", loc=(0, 0, 2), scale=(0.6, 0.6, 1.5), color="#E6E8EC", vertices=48)
add("cone", "Ніс", loc=(0, 0, 4.1), scale=(0.6, 0.6, 0.6), color="#D9342B", vertices=48)
add("cylinder", "Ілюмінатор", loc=(0, -0.55, 2.6), rot=(90, 0, 0), scale=(0.25, 0.25, 0.08), color="#8EC5F0", vertices=48)
for i, a in enumerate((0, 120, 240)):
    r = math.radians(a)
    add("cube", "Крило %d" % (i + 1), loc=(0.75 * math.cos(r), 0.75 * math.sin(r), 0.8),
        rot=(0, 0, a), scale=(0.45, 0.06, 0.45), color="#D9342B")
add("cone", "Полум’я", loc=(0, 0, 0.15), rot=(180, 0, 0), scale=(0.45, 0.45, 0.6), color="#F7CE46", vertices=48)
''' + SMOOTH

GROUP_ROCKET = ROCKET + '''
bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
_e = bpy.context.active_object
_e.name = "Ракета"
for _o in list(bpy.data.objects):
    if _o.type == "MESH":
        _o.parent = _e
'''

MATERIALS = '''
clean(cam=(7, -7, 4.5), target=(0, 0, 1.1))
t = add("cube", "Стільниця", loc=(0, 0, 0.9), scale=(1.6, 1.0, 0.06), color="#9A6232")
mat(t, hexc("#9A6232"), "Дерево", rough=0.55)
for i, (x, y) in enumerate([(-1.45, -0.85), (1.45, -0.85), (-1.45, 0.85), (1.45, 0.85)]):
    l = add("cube", "Ніжка %d" % (i + 1), loc=(x, y, 0.42), scale=(0.07, 0.07, 0.42))
    l.data.materials.append(t.data.materials[0])
g = add("cylinder", "Склянка", loc=(-0.7, 0, 1.36), scale=(0.25, 0.25, 0.4), vertices=64)
mm = mat(g, (0.85, 0.95, 1.0), "Скло", rough=0.02)
_b = next(n for n in mm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
_b.inputs["Transmission Weight"].default_value = 1.0
_b.inputs["IOR"].default_value = 1.45
s = add("uv_sphere", "Куля", loc=(0.6, 0.1, 1.36), scale=(0.4, 0.4, 0.4), segments=64, ring_count=32)
mat(s, (0.9, 0.75, 0.35), "Метал (золото)", metal=1.0, rough=0.2)
c = add("cube", "Кубик", loc=(0.2, -0.6, 1.16), scale=(0.2, 0.2, 0.2), rot=(0, 0, 25))
mat(c, hexc("#D9342B"), "Пластик", rough=0.35)
''' + SMOOTH

PAWN = '''
clean(cam=(5, -5, 3.6), target=(0, 0, 1.0))
add("cylinder", "Основа", loc=(0, 0, 0.12), scale=(0.75, 0.75, 0.12), color="#E6E8EC", vertices=64)
add("torus", "Кільце", loc=(0, 0, 0.28), scale=(0.62, 0.62, 0.62), color="#E6E8EC", major_segments=64, minor_segments=24,
    major_radius=1, minor_radius=0.2)
add("cone", "Тулуб", loc=(0, 0, 0.95), scale=(0.5, 0.5, 0.75), color="#E6E8EC", vertices=64)
add("cylinder", "Комірець", loc=(0, 0, 1.55), scale=(0.38, 0.38, 0.05), color="#E6E8EC", vertices=64)
add("uv_sphere", "Голова", loc=(0, 0, 1.92), scale=(0.36, 0.36, 0.36), color="#E6E8EC", segments=64, ring_count=32)
''' + SMOOTH

LAMP = '''
clean(cam=(6, -6, 4.5), target=(0, 0, 1.4))
add("cylinder", "Основа", loc=(0, 0, 0.05), scale=(0.7, 0.7, 0.05), color="#3A3D42", vertices=64)
add("cylinder", "Ніжка", loc=(0, 0, 1.1), scale=(0.06, 0.06, 1.05), color="#8C8F94", vertices=32)
add("cone", "Абажур", loc=(0, 0, 2.35), scale=(0.75, 0.75, 0.45), color="#F7CE46", vertices=64, radius1=1, radius2=0.45)
add("uv_sphere", "Лампочка", loc=(0, 0, 2.0), scale=(0.18, 0.18, 0.18), color="#FFF4C2", segments=32, ring_count=16)
''' + SMOOTH


def scene_with(base, *extra):
    return base + "".join(extra)


# анімації: кадри задаються прямо в коді сцени
SPIN = '''
clean(cam=(7, -7, 4.5), target=(0, 0, 1))
c = add("cube", "Куб", loc=(0, 0, 1), color="#E8772E")
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, 72
c.rotation_euler = (0, 0, 0); c.keyframe_insert("rotation_euler", frame=1)
c.rotation_euler = (0, 0, math.radians(360)); c.keyframe_insert("rotation_euler", frame=72)
c.scale = (1, 1, 1); c.keyframe_insert("scale", frame=1)
c.scale = (1.4, 1.4, 1.4); c.keyframe_insert("scale", frame=36)
c.scale = (1, 1, 1); c.keyframe_insert("scale", frame=72)
'''

BOUNCE = '''
clean(cam=(9, -9, 5), target=(0, 0, 1.3))
b = add("uv_sphere", "М’яч", loc=(-4, 0, 3), scale=(0.5, 0.5, 0.5), color="#E8772E", segments=48, ring_count=24)
bpy.context.view_layer.objects.active = b
bpy.ops.object.shade_smooth()
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, 96
pts = [(1, -4, 3.0), (16, -2.6, 0.5), (32, -1.2, 2.2), (48, 0.2, 0.5), (60, 1.4, 1.4), (72, 2.6, 0.5), (84, 3.4, 0.9),
       (96, 4.2, 0.5)]
for f, x, z in pts:
    b.location = (x, 0, z)
    b.keyframe_insert("location", frame=f)
'''

ORBIT_TAIL = '''
bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
_piv = bpy.context.active_object
_piv.name = "Центр обертання"
_cam = bpy.data.objects["Camera"]
_cam.parent = _piv
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, 120
_piv.rotation_euler = (0, 0, 0); _piv.keyframe_insert("rotation_euler", frame=1)
_piv.rotation_euler = (0, 0, math.radians(360)); _piv.keyframe_insert("rotation_euler", frame=121)
for fc in _piv.animation_data.action.fcurves:
    for k in fc.keyframe_points:
        k.interpolation = "LINEAR"
'''


def linear(name):
    return f'''
for fc in bpy.data.objects["{name}"].animation_data.action.fcurves:
    for k in fc.keyframe_points:
        k.interpolation = "LINEAR"
'''


FINISH = '''
ground()
world()
sun()
bpy.context.scene.camera = bpy.data.objects["Camera"]
'''


def zrazok(lesson, name, scene, png=True, anim=None, engine=None, res=(1280, 720), samples=64, stl=None):
    """Готовий зразок у «Додатки/<урок>/Зразок — name.blend» + рендер PNG (+ анімація .mp4/.gif, + .stl).
    Повертає шлях до PNG (або None). Уже зроблені файли не перебудовуємо (видаліть, щоб перезібрати)."""
    d = os.path.join(ADD_DIR, LESSON[lesson])
    os.makedirs(d, exist_ok=True)
    base = os.path.join(d, f"Зразок — {name}")
    code = scene + FINISH
    if stl:
        code += f'''
bpy.ops.object.select_all(action="DESELECT")
for _o in bpy.data.objects:
    if _o.type == "MESH" and _o.name != "Підлога":
        _o.select_set(True)
bpy.ops.wm.stl_export(filepath=r"{base}.stl", export_selected_objects=True)
'''
    need = not os.path.exists(base + ".blend") or (png and not os.path.exists(base + ".png")) or \
        (anim and not os.path.exists(base + anim))
    if need:
        bmake(code, blend=base + ".blend", png=(base + ".png") if png else None,
              anim=(base + anim) if anim else None, engine=engine or ("BLENDER_EEVEE" if anim else "CYCLES"),
              res=res if not anim else (854, 480), samples=samples)
    print("✓ " + base)
    return base + ".png" if png else None


def deck(lesson, big, sub, notes=""):
    d = Deck(LESSON[lesson].split(". ", 1)[1], kind="info", topic="3D-графіка · Blender")
    return d


def save(d, lesson):
    out = os.path.join(OUT_DIR, LESSON[lesson] + ".html")
    print(d.save(out), len(d.slides))


def zrazky_slide(d, lesson):
    """«Готові зразки»: рендери з «Додатків» + назви файлів. Ставимо перед «Як оцінюємо»."""
    folder = os.path.join(ADD_DIR, LESSON[lesson])
    pngs = sorted(glob.glob(os.path.join(folder, "Зразок — *.png")))
    if not pngs:
        return
    s = d.slide("Готові зразки",
                "Готові файли Blender — у сховищі: «Презентації уроків/9 клас/Додатки/" + LESSON[lesson] + "».\n"
                ".blend відкривається в Blender (Файл → Відкриття…): видно всі об’єкти в «Структурі», їхні розміри "
                "у «Властивостях», анімацію на таймлайні. PNG — рендер результату, .mp4 — відео анімації.\n"
                "Показуємо зразок перед самостійною роботою або для самоперевірки.")
    s.h2("Готові зразки")
    s.sub("Папка <b>Додатки / " + LESSON[lesson] + "</b>: .blend, рендер .png" +
          (", відео .mp4" if glob.glob(os.path.join(folder, "*.mp4")) else ""))
    n = min(len(pngs), 6)
    cols = n if n <= 3 else 3
    rows = (n + cols - 1) // cols
    cw = (1664 - 40 * (cols - 1)) // cols
    ch = (700 - 30 * (rows - 1)) // rows
    for i, p in enumerate(pngs[:6]):
        x = 128 + (i % cols) * (cw + 40)
        y = 290 + (i // cols) * (ch + 30)
        ih = ch - 64
        s.raw(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{cw}px;height:{ih}px;background:#e9edf2;'
              f'border:2px solid #2F3033;border-radius:10px;overflow:hidden;box-sizing:border-box;display:flex;'
              f'align-items:center;justify-content:center"><img alt="" src="{data_uri(p)}" '
              f'style="max-width:100%;max-height:100%"></div>')
        s.text(x, y + ih + 8, cw, 56, os.path.basename(p)[len("Зразок — "):-4], size=24, color=INK2, align="center",
               lh=1.15)


def render_img(s, x, y, w, png, h=None, label=None):
    """Рендер (PNG із «Додатків») на слайді в рамці."""
    from PIL import Image
    im = Image.open(png)
    hh = h or int(w * im.height / im.width)
    s.raw(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{hh}px;border:2px solid #2F3033;'
          f'border-radius:12px;overflow:hidden;box-sizing:border-box;background:#e9edf2">'
          f'<img alt="" src="{data_uri(png)}" style="width:100%;height:100%;object-fit:cover"></div>')
    if label:
        s.text(x, y + hh + 8, w, 44, label, size=24, color=INK2, align="center")
    return hh
