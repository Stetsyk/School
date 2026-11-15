"""Спільні малюнки для колод про текстові документи (5–6 клас): умовні фото, хом'як, сторінки з обтіканням."""
import math

from deck import ORANGE

# ---------- умовні «фото» ----------

LANDSCAPE = ('<rect width="160" height="120" fill="#BFD8F5"/><circle cx="118" cy="34" r="16" fill="#F0A55E"/>'
             '<path d="M0 92 Q40 58 80 86 T160 78 V120 H0 Z" fill="#7FB07A"/>'
             '<path d="M0 104 Q50 84 100 100 T160 98 V120 H0 Z" fill="#5E9460"/>')

FOREST = ('<rect width="160" height="120" fill="#CFE3F7"/><rect y="96" width="160" height="24" fill="#7FB07A"/>'
          + "".join(f'<rect x="{x + 7}" y="78" width="6" height="22" fill="#7A4B2A"/>'
                    f'<polygon points="{x},84 {x + 10},{40 + (x * 7) % 18} {x + 20},84" fill="#3F7A4A"/>'
                    for x in (6, 30, 54, 78, 102, 126)))

# хом'як: еліпси (cx, cy, rx, ry, колір) у порядку малювання — потрібні і для SVG, і для «пікселів»
HAMSTER_PARTS = [
    ("rect", 0, 0, 160, 120, "#F6E0C6"),
    ("rect", 0, 100, 160, 20, "#E9C98F"),
    ("ell", 52, 44, 11, 11, "#C97F3C"), ("ell", 108, 44, 11, 11, "#C97F3C"),
    ("ell", 52, 44, 6, 6, "#F2B6A8"), ("ell", 108, 44, 6, 6, "#F2B6A8"),
    ("ell", 80, 82, 48, 30, "#D9944F"),
    ("ell", 80, 90, 28, 18, "#F5DDBF"),
    ("ell", 80, 60, 34, 27, "#D9944F"),
    ("ell", 60, 70, 10, 8, "#F5DDBF"), ("ell", 100, 70, 10, 8, "#F5DDBF"),
    ("ell", 68, 56, 4.5, 4.5, "#2F3033"), ("ell", 92, 56, 4.5, 4.5, "#2F3033"),
    ("ell", 69.5, 54.5, 1.5, 1.5, "#FFFFFF"), ("ell", 93.5, 54.5, 1.5, 1.5, "#FFFFFF"),
    ("ell", 80, 66, 3.5, 2.5, "#E58C8C"),
    ("ell", 64, 104, 7, 4, "#F2B6A8"), ("ell", 96, 104, 7, 4, "#F2B6A8"),
]


def _hamster_svg():
    out = []
    for p in HAMSTER_PARTS:
        if p[0] == "rect":
            _, x, y, w, h, col = p
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{col}"/>')
        else:
            _, cx, cy, rx, ry, col = p
            out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{col}"/>')
    return "".join(out)


ART = {"landscape": LANDSCAPE, "hamster": _hamster_svg(), "forest": FOREST}


def pic(s, x, y, w, h, art="landscape", squash=False, handles=False, corner_hl=False, side_hl=False, border=True):
    """Умовне фото. squash=True — розтягнуте без збереження пропорцій (як боковим маркером)."""
    par = "none" if squash else "xMidYMid slice"
    bd = "border:2px solid #3E3F42;" if border else ""
    s.raw(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;{bd}box-sizing:border-box;'
          f'overflow:hidden;border-radius:4px"><svg width="100%" height="100%" viewBox="0 0 160 120" '
          f'preserveAspectRatio="{par}">{ART[art]}</svg></div>')
    if handles:
        pts = [(0, 0), (.5, 0), (1, 0), (0, .5), (1, .5), (0, 1), (.5, 1), (1, 1)]
        for px, py in pts:
            corner = px in (0, 1) and py in (0, 1)
            hl = (corner and corner_hl) or (not corner and side_hl)
            col = ORANGE if hl else "#FFFFFF"
            sz = 26 if hl else 18
            s.raw(f'<div style="position:absolute;left:{x + px * w - sz / 2}px;top:{y + py * h - sz / 2}px;'
                  f'width:{sz}px;height:{sz}px;background:{col};border:3px solid #2F6FB7;box-sizing:border-box"></div>')


def _hamster_at(fx, fy):
    col = None
    for p in HAMSTER_PARTS:
        if p[0] == "rect":
            _, x, y, w, h, c = p
            if x <= fx <= x + w and y <= fy <= y + h:
                col = c
        else:
            _, cx, cy, rx, ry, c = p
            if ((fx - cx) / rx) ** 2 + ((fy - cy) / ry) ** 2 <= 1:
                col = c
    return col


def _landscape_at(fx, fy):
    hill1 = 92 - 22 * math.sin(math.pi * fx / 80) if fx < 80 else 86 - 8 * math.sin(math.pi * (fx - 80) / 80)
    hill2 = 104 - 12 * math.sin(math.pi * fx / 100)
    if (fx - 118) ** 2 + (fy - 34) ** 2 < 16 ** 2:
        return "#F0A55E"
    if fy > hill2:
        return "#5E9460"
    if fy > hill1:
        return "#7FB07A"
    return "#BFD8F5"


def pix(s, x, y, w, h, art="landscape", cols=16, rows=12):
    """Те саме «фото», розтягнуте з маленького: видно квадратики."""
    at = _hamster_at if art == "hamster" else _landscape_at
    cells = []
    for r in range(rows):
        for cc in range(cols):
            fx, fy = (cc + .5) / cols * 160, (r + .5) / rows * 120
            cells.append(f'<div style="background:{at(fx, fy)}"></div>')
    s.raw(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;display:grid;'
          f'grid-template-columns:repeat({cols},1fr);grid-template-rows:repeat({rows},1fr);border:2px solid #3E3F42;'
          f'box-sizing:border-box;overflow:hidden">' + "".join(cells) + "</div>")


# ---------- сторінки ----------

def line(s, lx, ly, ww, col="#AEB6C1", h=10):
    s.raw(f'<div style="position:absolute;left:{lx}px;top:{ly}px;width:{ww}px;height:{h}px;border-radius:{h // 2}px;'
          f'background:{col}"></div>')


def sheet(s, x, y, w, h):
    s.raw(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:#FBFCFD;'
          f'border:2px solid #3E3F42;border-radius:8px;box-sizing:border-box;box-shadow:0 10px 30px rgba(30,40,60,0.18)"></div>')


def wrap_page(s, x, y, w, h, mode, title=True, art="landscape", caption=False):
    """Мініатюра сторінки з фото та одним із видів розташування: inline, around, topbottom, behind."""
    sheet(s, x, y, w, h)
    m = 26
    lw = w - 2 * m
    cy = y + m
    if title:
        line(s, x + m + lw * .25, cy, lw * .5, "#4A4E55", 18)
        cy += 36
    step = 22
    if mode == "inline":
        for i in range(3):
            line(s, x + m, cy, lw * (0.95 if i < 2 else .6)); cy += step
        line(s, x + m, cy + 30, lw * .3)
        pic(s, x + m + lw * .32, cy, 60, 44, art)
        line(s, x + m + lw * .32 + 70, cy + 30, lw - lw * .32 - 70)
        cy += 56
        while cy < y + h - m - 10:
            line(s, x + m, cy, lw * .95); cy += step
    elif mode == "around":
        pw, ph = int(lw * .42), 110
        pic(s, x + m, cy, pw, ph, art)
        yy = cy
        if caption:
            line(s, x + m + pw * .15, cy + ph + 8, pw * .7, "#7C8591", 7)
        while yy < cy + ph + (16 if caption else 0):
            line(s, x + m + pw + 16, yy, lw - pw - 16); yy += step
        while yy < y + h - m - 10:
            line(s, x + m, yy, lw); yy += step
    elif mode == "topbottom":
        for i in range(2):
            line(s, x + m, cy, lw); cy += step
        ph = 100
        pic(s, x + m + lw * .15, cy + 4, lw * .7, ph, art)
        cy += ph + 16
        while cy < y + h - m - 10:
            line(s, x + m, cy, lw); cy += step
    elif mode == "behind":
        pic(s, x + m + 10, cy + 10, lw - 20, h - (cy - y) - m - 20, art, border=False)
        s.raw(f'<div style="position:absolute;left:{x + m + 10}px;top:{cy + 10}px;width:{lw - 20}px;'
              f'height:{h - (cy - y) - m - 20}px;background:rgba(251,252,253,0.55)"></div>')
        while cy < y + h - m - 10:
            line(s, x + m, cy, lw, "#5C626B"); cy += step
    elif mode == "text":
        while cy < y + h - m - 10:
            line(s, x + m, cy, lw); cy += step
