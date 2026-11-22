"""Покрокові скріни Krita: справжній чіткий скрін (kritashot, scale=2) → вирізані шматки → помаранчеві рамки й
номери кроків (kroky.compose) — такі самі, як на скрінах Google Документів. На слайді: s.gshot(...) + s.gsteps(...).

Усі координати — у точках екрана Krita 1366 × 768 (українська Krita 5.2, без панелі «Набори пензлів», тоді
«Шари» на всю висоту праворуч). Готові місця кнопок — нижче (TOOL, MENU, LAYERS…), щоб не міряти щоразу.

    from kritakroky import kk, TOOL, box, row_box
    png = kk(сценарій, xdo, parts=[(0, 0, 400, 300)], marks=[box(TOOL["Пензель"], "right")])
"""
import hashlib
import json
import os

from PIL import Image

from kritashot import kshot, CACHE
from kroky import compose

HERE = os.path.dirname(os.path.abspath(__file__))
AWAY = "mousemove 1300 760"     # мишку — в куток, щоб не заважала

# --- панель інструментів ліворуч: центри значків -------------------------------------------------------------
_C1, _C2 = 12, 36
TOOL = {
    "Вибір фігур": (_C1, 85), "Текст": (_C2, 85),
    "Пензель": (_C1, 139), "Лінія": (_C2, 139),
    "Прямокутник": (_C1, 164), "Еліпс": (_C2, 164),
    "Багатокутник": (_C1, 187), "Ламана": (_C2, 187),
    "Трансформування": (_C1, 264), "Переміщення": (_C2, 264),
    "Обрізання": (_C1, 289),
    "Градієнт": (_C1, 318), "Піпетка": (_C2, 318),
    "Заливка": (_C1, 367),
    "Прямокутне виділення": (_C1, 452), "Еліптичне виділення": (_C2, 452),
    "Масштаб": (_C1, 554), "Рука": (_C2, 554),
}
# id дій Krita для тих самих інструментів (кроки сценарію {"tool": …})
TOOL_ID = {"Вибір фігур": "InteractionTool", "Текст": "SvgTextTool", "Пензель": "KisToolBrush",
           "Лінія": "KisToolLine", "Прямокутник": "KisToolRectangle", "Еліпс": "KisToolEllipse",
           "Багатокутник": "KisToolPolygon", "Переміщення": "KisToolMove", "Трансформування": "KisToolTransform",
           "Піпетка": "KritaSelected/KisToolColorSampler", "Заливка": "KritaFill/KisToolFill",
           "Прямокутне виділення": "KisToolSelectRectangular", "Еліптичне виділення": "KisToolSelectElliptical",
           "Масштаб": "ZoomTool"}

# --- меню вгорі (рамки x0, y0, x1, y1) ------------------------------------------------------------------------
MENU = {"Файл": (4, 1, 47, 20), "Зміни": (54, 1, 103, 20), "Шар": (294, 1, 331, 20), "Вибір": (339, 1, 384, 20)}

# пункти меню «Файл» (рамки)
FILE_MENU = {k: (24, y - 12, 405, y + 12) for k, y in
             {"Створити": 34, "Відкрити": 59, "Зберегти": 111, "Зберегти як": 136, "Експортувати": 216}.items()}

# --- верхня панель ------------------------------------------------------------------------------------------
TOP = {"Колір": (175, 25, 206, 55), "Непрозорість пензля": (713, 26, 921, 54), "Розмір пензля": (960, 26, 1170, 54),
       "Гумка": (630, 30, 655, 55)}

# --- кольори (праворуч угорі) -------------------------------------------------------------------------------
COLOR = (1104, 96, 1352, 210)       # коло й трикутник «Розширений вибір кольору»

# --- панель «Шари» (коли панель пензлів сховано) -----------------------------------------------------------
LAYERS = {"Режим": (1105, 362, 1332, 387), "Непрозорість": (1105, 396, 1320, 421),
          "+": (1110, 708, 1131, 732), "▾ біля +": (1132, 708, 1150, 732), "Копія": (1153, 708, 1176, 732),
          "Нижче": (1184, 708, 1209, 732), "Вище": (1216, 708, 1241, 732), "Властивості": (1246, 708, 1290, 732),
          "Видалити": (1338, 708, 1361, 732)}
LAYER_PANEL = (1100, 336, 1366, 742)   # уся панель «Шари»
ROW0, ROW_H = 439, 27                  # центр першого (верхнього) рядка шару і висота рядка
DOC = (72, 89, 1086, 721)              # ділянка полотна
DOC_1200 = (186, 110, 970, 700)        # документ 1200 × 900 при масштабі 1,3 (shary6.land_steps)


def row_y(i):
    return ROW0 + ROW_H * i


def row_box(i, part="row", side="left"):
    """Рамка рядка шару i (0 — верхній): part = row · eye · name."""
    y = row_y(i)
    x0, x1 = {"row": (1104, 1362), "eye": (1107, 1128), "name": (1190, 1290)}[part]
    return (x0, y - 12, x1, y + 12, side)


def box(c, side="right", half=13):
    """Рамка навколо точки-центру (значок інструмента) або готової рамки (x0, y0, x1, y1)."""
    if len(c) == 4:
        return (*c, side)
    x, y = c
    return (x - half, y - half, x + half, y + half, side)


def kfull(scenario, xdo=None):
    """Чіткий скрін усього вікна Krita (PNG 2732 × 1536). Для kwin множте crop на 2."""
    return kshot(scenario, xdo, scale=2)


def kk(scenario, xdo=None, parts=((0, 0, 1366, 768),), marks=(), nums=None, layout=None):
    """Справжній скрін Krita → шматки parts (у точках) → позначки marks (x0, y0, x1, y1, бік) з номерами кроків.
    nums: None — 1, 2, 3…; кортеж — свої номери; False — без номерів. layout="row" — шматки поруч."""
    png = kshot(scenario, xdo, scale=2)
    src = json.dumps([png, list(parts), list(marks), nums, layout], ensure_ascii=False)
    src += open(os.path.join(HERE, "kroky.py"), encoding="utf-8").read()
    h = hashlib.md5(src.encode()).hexdigest()[:14]
    out = os.path.join(CACHE, f"kroky-{h}.png")
    if not os.path.exists(out):
        im = Image.open(png).convert("RGB")
        crops = [(tuple(p), im.crop(tuple(v * 2 for v in p))) for p in parts]
        compose(crops, list(marks), nums, layout == "row", out, "krita")
    open(out + ".title", "w").write("Krita")
    return out


# --- типові слайди ------------------------------------------------------------------------------------------
def how(d, title, notes, steps, png, side=True, start=1, sub=None, w_steps=560, maxh=None, size=30):
    """Слайд «як це зробити»: кроки з помаранчевими номерами + скрін Krita з такими самими номерами.
    side=True — кроки ліворуч, скрін праворуч; False — кроки рядком угорі, скрін під ними на всю ширину."""
    import gdocs  # noqa: F401  — s.gshot, s.gsteps
    s = d.slide(title, notes)
    if len(title) > 34:
        s.h2(title, size=60)
    else:
        s.h2(title)
    top = 210
    if sub:
        s.sub(sub)
        top = 270
    if side:
        s.gsteps(steps, x=128, y=top + 10, w=w_steps, size=size, start=start)
        x = 128 + w_steps + 50
        s.gshot(x, top, 1792 - x, png, maxh=maxh or (1010 - top), align="center")
    else:
        s.gsteps_row(steps, y=top, size=min(size, 28), start=start)
        s.gshot(128, top + 130, 1664, png, maxh=maxh or (1000 - top - 130), align="center")
    return s
