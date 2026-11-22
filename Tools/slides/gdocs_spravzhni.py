"""Справжні скріни Google Документів (український інтерфейс), зняті в Chrome учителя.

Як знято: документ у Google Диску (папка «Скріни для уроків»), масштаб документа 150 %, дія виконана руками
(через Claude in Chrome), потім ділянку екрана знято з подвійною чіткістю (Retina) — файли в `gdocs-spravzhni/`.

Як це працює:
- RAW[назва] — ділянка екрана (x0, y0, x1, y1) у точках сторінки, яку покриває файл `gdocs-spravzhni/<назва>.png`;
- SHOT[ключ] — з яких шматків (назва, кроп у точках екрана) складається скрін і де позначки (рамка в точках екрана, бік номера).
  Кілька шматків ставимо один під одним: зверху панель/меню, знизу документ — так кнопка й текст поруч і великі.
- real(ключ, nums) → шлях до готового PNG (масштаб 2, як у gdocs.Doc.shot), номери кроків — помаранчеві, як у gsteps.

Знімати нові: відкрий документ, зроби дію, сховай мишку, `computer zoom` з `save_to_disk`, скопіюй PNG сюди,
допиши RAW і SHOT. Координати бери зі звичайного скріна вкладки (1440 точок завширшки)."""
import hashlib
import json
import os
import tempfile

from PIL import Image

from kroky import compose

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "gdocs-spravzhni")
CACHE = os.path.join(os.environ.get("SLIDES_CACHE", os.path.join(tempfile.gettempdir(), "slides-cache")), "gdocs-spravzhni")

# назва файлу → ділянка екрана, яку він покриває (точки сторінки)
RAW = {
    "panel-format": (296, 64, 806, 268),
    "list-bullet-pokhid": (430, 64, 1220, 428),
    "tb-list-number": (900, 64, 1230, 106),
    "list-number-pokhid": (436, 450, 790, 592),
    "list-bullet-mlyntsi": (436, 288, 740, 428),
    "list-number-mlyntsi": (436, 450, 800, 592),
    "tabl4x6": (236, 32, 770, 300),
    "tabl3x5": (236, 32, 770, 290),
    "tablrow": (340, 262, 912, 552),
    "tablcol": (672, 262, 1350, 552),
    "tb-tablbold": (630, 64, 1290, 172),
    "tablbold": (440, 326, 920, 420),
    "obyednaty": (438, 288, 1102, 640),
    "tb-align": (860, 64, 1100, 144),
    "align-center": (440, 288, 740, 342),
    "tb-interval": (950, 64, 1250, 234),
    "interval": (440, 390, 832, 450),
    "file-top": (54, 32, 378, 100),
    "file-nalasht": (54, 546, 378, 718),
    "pdf": (54, 32, 640, 516),
    "nalasht-landscape": (522, 26, 918, 662),
    "tb-shryft": (540, 64, 1045, 144),
    "shryft": (440, 288, 720, 340),
    "zobr": (236, 32, 822, 294),
    "zobr-panel": (1106, 70, 1422, 726),
    "vydil-hamster": (438, 312, 774, 554),
    "wrap-hamster": (438, 312, 790, 612),
    "zobr-panel-autumn": (1106, 70, 1422, 726),
    "wrap-autumn": (438, 312, 866, 664),
}

# Позначки вставок і пунктів, які повторюються
INS = (240, 35, 312, 56, "left")            # меню «Вставити»
FILE = (60, 35, 100, 56, "left")            # меню «Файл»
TB_BULLET = ("list-bullet-pokhid", (912, 66, 1218, 104))
TB_NUMBER = ("tb-list-number", (906, 66, 1226, 104))

# ключ → шматки й позначки. Позначка: (x0, y0, x1, y1, бік) — бік номера: left/right/top/bottom;
# "nonum" — рамка без номера (і без свого кроку). layout="row" — шматки поруч, інакше один під одним.
SHOT = {
    "panel-format": dict(
        parts=[("panel-format", (300, 66, 804, 100)), ("panel-format", (392, 234, 640, 262))],
        marks=[(424, 242, 442, 259, "bottom"), (444, 72, 530, 98, "top"), (570, 72, 604, 98, "top"),
               (643, 72, 733, 98, "top"), (738, 70, 768, 100, "top")]),
    "list-bullet-pokhid": dict(
        parts=[TB_BULLET, ("list-bullet-pokhid", (440, 290, 680, 427))],
        marks=[(515, 318, 664, 424, "right"), (1036, 72, 1062, 98, "right")]),
    "list-number-pokhid": dict(
        parts=[TB_NUMBER, ("list-number-pokhid", (440, 452, 786, 588))],
        marks=[(515, 482, 760, 587, "right"), (1080, 71, 1108, 99, "right")]),
    "list-bullet-mlyntsi": dict(
        parts=[TB_BULLET, ("list-bullet-mlyntsi", (440, 290, 736, 426))],
        marks=[(515, 318, 708, 424, "right"), (1036, 72, 1062, 98, "right")]),
    "list-number-mlyntsi": dict(
        parts=[TB_NUMBER, ("list-number-mlyntsi", (440, 452, 796, 588))],
        marks=[(515, 482, 742, 587, "right"), (1080, 71, 1108, 99, "right")]),
    "tabl4x6": dict(
        parts=[("tabl4x6", (237, 33, 768, 298))],
        marks=[INS, (240, 98, 554, 127, "left"), (562, 156, 634, 264, "bottom")]),
    "tabl3x5": dict(
        parts=[("tabl3x5", (237, 33, 768, 288))],
        marks=[INS, (240, 98, 554, 127, "left"), (562, 156, 616, 246, "bottom")]),
    "tablrow": dict(
        parts=[("tablrow", (440, 312, 910, 506))],
        marks=[(447, 475, 545, 502, "left"), (562, 345, 905, 377, "right")]),
    "tablcol": dict(
        parts=[("tablcol", (900, 312, 1338, 448))],
        marks=[(916, 389, 988, 416, "left"), (990, 409, 1331, 440, "right")]),
    "tablbold": dict(
        parts=[("tb-tablbold", (632, 66, 1288, 171)), ("tablbold", (442, 329, 920, 418))],
        marks=[(447, 331, 918, 359, "left"), (640, 71, 668, 99, "bottom"), (1247, 71, 1274, 99, "bottom"),
               (1013, 112, 1052, 140, "left")]),
    "obyednaty": dict(
        parts=[("obyednaty", (440, 290, 1100, 639))],
        marks=[(447, 360, 745, 416, "left"), (748, 603, 1088, 634, "left")]),
    "align-center": dict(
        parts=[("tb-align", (862, 66, 1098, 142)), ("align-center", (442, 290, 738, 336))],
        marks=[(447, 294, 695, 336, "right"), (916, 70, 952, 100, "right"), (948, 108, 980, 136, "bottom")]),
    "interval1,5": dict(
        parts=[("tb-interval", (952, 66, 1248, 232)), ("interval", (442, 392, 826, 446))],
        marks=[(447, 395, 826, 446, "right"), (958, 70, 988, 100, "left"), (960, 172, 1244, 202, "right")]),
    "file-nalasht": dict(
        parts=[("file-top", (56, 34, 376, 99)), ("file-nalasht", (56, 548, 376, 716))],
        marks=[FILE, (58, 646, 374, 677, "right")]),
    "pdf": dict(
        parts=[("pdf", (56, 34, 638, 470))],
        marks=[FILE, (58, 243, 374, 273, "left"), (378, 282, 634, 312, "right")]),
    "nalasht-landscape": dict(
        parts=[("nalasht-landscape", (523, 34, 917, 318)), ("nalasht-landscape", (523, 560, 917, 618))],
        marks=[(682, 281, 795, 311, "bottom"), (826, 571, 894, 609, "left")]),
    "shryft20": dict(
        parts=[("tb-shryft", (542, 66, 1043, 142)), ("shryft", (442, 290, 718, 338))],
        marks=[(447, 293, 715, 337, "right"), (570, 72, 604, 98, "top"), (640, 71, 668, 99, "top"),
               (916, 70, 952, 100, "top"), (948, 108, 980, 136, "nonum")]),
    "zobr": dict(
        layout="row",
        parts=[("zobr", (237, 33, 820, 292)), ("zobr-panel", (1108, 120, 1420, 440)), ("zobr-panel", (1108, 672, 1420, 724))],
        marks=[INS, (240, 66, 554, 96, "left"), (560, 104, 818, 136, "bottom"), (1126, 138, 1405, 176, "bottom"),
               (1268, 320, 1405, 432, "nonum"), (1311, 677, 1409, 717, "nonum")]),
    "zobr-autumn": dict(
        layout="row",
        parts=[("zobr", (237, 33, 820, 292)), ("zobr-panel-autumn", (1108, 120, 1420, 440)), ("zobr-panel-autumn", (1108, 672, 1420, 724))],
        marks=[INS, (240, 66, 554, 96, "left"), (560, 104, 818, 136, "bottom"), (1126, 138, 1405, 176, "bottom"),
               (1217, 196, 1405, 320, "nonum"), (1311, 677, 1409, 717, "nonum")]),
    "vydil-hamster": dict(parts=[("vydil-hamster", (439, 313, 766, 553))], marks=[]),
    "wrap-hamster": dict(
        parts=[("wrap-hamster", (439, 313, 762, 611))],
        marks=[(450, 342, 762, 548, "left"), (458, 561, 500, 589, "bottom"), (456, 410, 661, 444, "right")]),
    "wrap-autumn": dict(
        parts=[("wrap-autumn", (439, 330, 865, 663))],
        marks=[(450, 342, 855, 602, "left"), (458, 615, 500, 643, "bottom"), (456, 464, 661, 498, "right")]),
}


def _scale(name):
    x0, y0, x1, y1 = RAW[name]
    w, h = Image.open(os.path.join(RAW_DIR, name + ".png")).size
    return w / (x1 - x0), h / (y1 - y0)


def real(key, nums=None):
    """Готовий PNG скріна `key` з номерами кроків. nums: None → 1, 2, 3…; False → без номерів; кортеж → свої номери
    (None в кортежі — рамка без номера)."""
    spec = SHOT[key]
    src = json.dumps([spec, [RAW[p[0]] for p in spec["parts"]], nums], ensure_ascii=False)
    src += "".join(str(os.path.getmtime(os.path.join(RAW_DIR, p[0] + ".png"))) for p in spec["parts"])
    src += open(__file__, encoding="utf-8").read()
    h = hashlib.md5(src.encode()).hexdigest()[:12]
    os.makedirs(CACHE, exist_ok=True)
    out = os.path.join(CACHE, f"{key}-{h}.png")
    if os.path.exists(out):
        return out

    S = 2
    crops = []
    for name, (cx0, cy0, cx1, cy1) in spec["parts"]:
        sx, sy = _scale(name)
        rx0, ry0 = RAW[name][:2]
        im = Image.open(os.path.join(RAW_DIR, name + ".png")).convert("RGB")
        im = im.crop((round((cx0 - rx0) * sx), round((cy0 - ry0) * sy), round((cx1 - rx0) * sx), round((cy1 - ry0) * sy)))
        im = im.resize((round((cx1 - cx0) * S), round((cy1 - cy0) * S)), Image.LANCZOS)
        crops.append(((cx0, cy0, cx1, cy1), im))
    compose(crops, spec["marks"], nums, spec.get("layout") == "row", out, key)
    open(out + ".title", "w").write("Google Документи")
    return out


if __name__ == "__main__":
    import sys
    for k in (sys.argv[1:] or SHOT):
        print(k, real(k))
