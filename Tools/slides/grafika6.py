"""Заготовки для колод 6 класу про графіку (І-11 … І-13): растрові малюнки (PIL) і векторні SVG,
які відкриваються в справжній Krita (kritashot.py). Файли кладуться в кеш (SLIDES_CACHE/krita-assets) — вони похідні."""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
import tempfile
ASSETS = os.path.join(os.environ.get("SLIDES_CACHE", os.path.join(tempfile.gettempdir(), "slides-cache")), "krita-assets")
os.makedirs(ASSETS, exist_ok=True)


def path(name):
    return os.path.join(ASSETS, name)


def emoji(stage=4, size=500, bg=None, mood="smile"):
    """Емодзі-мордочка поетапно: 1 — жовте коло, 2 — очі, 3 — усмішка, 4 — щічки. bg=None — прозоре тло."""
    k = 4
    S = size * k
    im = Image.new("RGBA", (S, S), bg or (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pad = int(S * 0.08)
    if stage >= 1:
        d.ellipse((pad, pad, S - pad, S - pad), fill="#F7CE46", outline="#E0A82E", width=int(S * 0.012))
    if stage >= 2:
        for cx in (0.36, 0.64):
            d.ellipse((S * cx - S * .045, S * .33, S * cx + S * .045, S * .45), fill="#2F3033")
    if stage >= 3:
        w = int(S * 0.028)
        if mood == "smile":
            d.arc((S * .28, S * .38, S * .72, S * .74), 20, 160, fill="#2F3033", width=w)
        else:
            d.arc((S * .32, S * .62, S * .68, S * .86), 200, 340, fill="#2F3033", width=w)
    if stage >= 4:
        for cx in (0.25, 0.75):
            d.ellipse((S * cx - S * .07, S * .52, S * cx + S * .07, S * .62), fill=(242, 140, 150, 170))
    im = im.resize((size, size), Image.LANCZOS)
    return im


def save_emoji(stage=4, size=500, name=None, bg=None, mood="smile"):
    p = path(name or f"emodzi_{stage}_{size}.png")
    emoji(stage, size, bg, mood).save(p)
    return p


def landscape_photo(w=800, h=600, name="krajevyd.png", seed=3):
    """«Фото»: небо з градієнтом, сонце, пагорби, дерева, шум — щоб було схоже на справжній знімок."""
    random.seed(seed)
    im = Image.new("RGB", (w, h))
    px = im.load()
    for y in range(h):
        t = y / h
        for x in range(w):
            if t < 0.6:
                r, g, b = 120 + 80 * t, 170 + 60 * t, 235 - 20 * t
            else:
                r, g, b = 90, 150, 80
            px[x, y] = (int(r), int(g), int(b))
    d = ImageDraw.Draw(im)
    d.ellipse((560, 70, 660, 170), fill=(255, 214, 120))
    d.polygon([(0, 380), (200, 260), (420, 360), (620, 250), (800, 330), (800, 600), (0, 600)], fill=(108, 160, 96))
    d.polygon([(0, 470), (300, 400), (560, 450), (800, 410), (800, 600), (0, 600)], fill=(82, 135, 72))
    for k in range(9):
        x = 60 + k * 85 + random.randint(-15, 15)
        y = 430 + random.randint(-20, 20)
        d.rectangle((x - 5, y, x + 5, y + 40), fill=(110, 75, 45))
        d.ellipse((x - 34, y - 60, x + 34, y + 14), fill=(52, 110 + random.randint(-15, 15), 60))
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    px = im.load()
    for y in range(h):
        for x in range(w):
            n = random.randint(-9, 9)
            r, g, b = px[x, y]
            px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)))
    p = path(name)
    im.save(p)
    return p


def pixel_heart(n=8, name="serdechko_8.png", scale=1):
    rows = ["........",
            ".##..##.",
            "########",
            "########",
            ".######.",
            "..####..",
            "...##...",
            "........"]
    im = Image.new("RGBA", (n, n), (255, 255, 255, 255))
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == "#":
                im.putpixel((x, y), (217, 52, 43, 255))
    if scale > 1:
        im = im.resize((n * scale, n * scale), Image.NEAREST)
    p = path(name)
    im.save(p)
    return p


ROCKET_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500">
  <circle id="zirka1" cx="70" cy="80" r="9" fill="#F7CE46"/>
  <circle id="zirka2" cx="420" cy="110" r="7" fill="#F7CE46"/>
  <circle id="zirka3" cx="90" cy="380" r="8" fill="#F7CE46"/>
  <circle id="zirka4" cx="410" cy="400" r="10" fill="#F7CE46"/>
  <circle id="zirka5" cx="380" cy="250" r="6" fill="#F7CE46"/>
  <polygon id="polumia" points="215,390 285,390 250,470" fill="#F0943A"/>
  <polygon id="krylo1" points="200,300 200,400 140,410" fill="#D9342B"/>
  <polygon id="krylo2" points="300,300 300,400 360,410" fill="#D9342B"/>
  <ellipse id="korpus" cx="250" cy="270" rx="58" ry="140" fill="#FFFFFF" stroke="#2F3033" stroke-width="4"/>
  <polygon id="nis" points="205,175 295,175 250,105" fill="#D9342B"/>
  <circle id="iliuminator" cx="250" cy="250" r="28" fill="#8EC5F2" stroke="#2F3033" stroke-width="4"/>
</svg>'''

HOUSE_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500">
  <rect id="stiny" x="110" y="230" width="280" height="200" fill="#C98F55" stroke="#2F3033" stroke-width="4"/>
  <polygon id="dakh" points="90,235 410,235 250,100" fill="#D9342B" stroke="#2F3033" stroke-width="4"/>
  <rect id="dveri" x="215" y="320" width="70" height="110" fill="#6E4A2E"/>
  <rect id="vikno" x="140" y="270" width="55" height="55" fill="#8EC5F2" stroke="#2F3033" stroke-width="3"/>
</svg>'''

SMILE_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
  <circle cx="20" cy="20" r="17" fill="#F7CE46" stroke="#E0A82E" stroke-width="1.2"/>
  <ellipse cx="14" cy="16" rx="2" ry="3" fill="#2F3033"/>
  <ellipse cx="26" cy="16" rx="2" ry="3" fill="#2F3033"/>
  <path d="M12 23 Q20 31 28 23" fill="none" stroke="#2F3033" stroke-width="1.6"/>
</svg>'''


def svg_file(svg, name):
    p = path(name)
    open(p, "w", encoding="utf-8").write(svg)
    return p


# ---------- вставлення скриншотів Krita у слайд ----------

def kwin(s, x, y, w, png, crop=None, border=True, shadow=True):
    """Скриншот Krita (або його частина crop=(x, y, w, h)) у слайді. Повертає функцію,
    яка переводить точку скриншота в координати слайда: at(px, py) -> (sx, sy)."""
    from deck import data_uri, DARK_BG
    from PIL import Image
    im = Image.open(png)
    cx, cy = 0, 0
    if crop:
        cx, cy, cw, ch = crop
        im = im.crop((cx, cy, cx + cw, cy + ch))
        import hashlib
        out = png[:-4] + "-" + hashlib.md5(str(crop).encode()).hexdigest()[:8] + ".png"
        im.save(out, optimize=True)
        png = out
    iw, ih = im.size
    sc = w / iw
    h = int(ih * sc)
    bd = f"border:2px solid {DARK_BG};" if border else ""
    sh = "box-shadow:0 14px 40px rgba(30,40,60,0.25);" if shadow else ""
    s.raw(f'<img alt="" src="{data_uri(png)}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
          f'{bd}{sh}border-radius:10px;box-sizing:border-box">')

    def at(px, py):
        return int(x + (px - cx) * sc), int(y + (py - cy) * sc)
    at.h = h
    at.sc = sc
    return at


def num(s, x, y, n, size=46, color="#B85F1E"):
    """Помаранчевий кружечок з номером (виноска на скриншоті); (x, y) — центр."""
    s.raw(f'<div style="position:absolute;left:{x - size // 2}px;top:{y - size // 2}px;width:{size}px;height:{size}px;'
          f'border-radius:50%;background:{color};display:flex;align-items:center;justify-content:center;'
          f'box-shadow:0 0 0 3px #fff"><p style="font-size:{int(size * .52)}px;font-weight:800;color:#fff">{n}</p></div>')


def ring(s, x, y, w, h, color="#F0943A", width=5, radius=10):
    """Рамка-підсвітка поверх скриншота."""
    s.raw(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border:{width}px solid {color};'
          f'border-radius:{radius}px;box-sizing:border-box;box-shadow:0 0 0 3px rgba(255,255,255,0.6)"></div>')


def ring_with_gap(gap=True, name=None, size=500):
    """Контур кола для досліду із заливкою: з щілиною фарба «витікає»."""
    im = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    d.ellipse((90, 90, 410, 410), outline=(47, 48, 51, 255), width=10)
    if gap:
        d.rectangle((395, 230, 420, 262), fill=(255, 255, 255, 255))
    p = path(name or f"kontur_{'shchilyna' if gap else 'tsilyi'}.png")
    im.save(p)
    return p


# Перетворення координат документа 500×500 у координати екрана Krita (1366×768, масштаб 100 %).
ORIGIN = (328, 156)


def scr(x, y):
    return ORIGIN[0] + int(x), ORIGIN[1] + int(y)


def stroke(points):
    """Команди xdotool для мазка пензлем через точки документа."""
    x0, y0 = scr(*points[0])
    cmds = [f"mousemove {x0} {y0}", "mousedown 1"]
    for (x, y) in points[1:]:
        sx, sy = scr(x, y)
        cmds.append(f"mousemove {sx} {sy}")
    cmds += ["mouseup 1", "sleep 0.3"]
    return cmds


def smile_points(cx=250, cy=280, rx=110, ry=90, a0=20, a1=160, n=14):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1))),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1)))) for i in range(n)]


LAND_PARTS = {
    "sonce": '<circle id="sonce" cx="380" cy="110" r="55" fill="#F7CE46"/>',
    "nebo": '<rect id="nebo" x="0" y="0" width="500" height="500" fill="#BFD8F5"/>',
    "hory": '<polygon id="hory" points="0,330 140,170 260,300 360,190 500,320 500,500 0,500" fill="#8D949E"/>',
    "khmara": '<ellipse id="khmara" cx="170" cy="120" rx="80" ry="34" fill="#FFFFFF"/>',
    "trava": '<rect id="trava" x="0" y="360" width="500" height="140" fill="#7FB07A"/>',
}


def landscape_svg(order):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500">'
            + "".join(LAND_PARTS[k] for k in order) + "</svg>")
