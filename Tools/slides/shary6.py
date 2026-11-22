"""Малюнки для колод 6 класу про шари й текст (І-14, І-15): краєвид із будинком, розкладений на шари,
і плакат до змагань. Кожна частина — окрема PNG того самого розміру з прозорим тлом, щоб у Krita її поклали
окремим шаром (kritashot: {"png_layer": [назва, шлях]})."""
import os

from PIL import Image, ImageDraw, ImageFont

from grafika6 import ASSETS

W, H = 1200, 900
K = 2  # малюємо вдвічі більше й зменшуємо — рівні краї
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# порядок у стопці знизу вгору (як на уроці: небо — найнижче, підпис — найвище)
LAND = ["небо", "трава", "сонце", "хмара", "будинок", "дерево", "підпис"]
SLUG = {"небо": "nebo", "трава": "trava", "сонце": "sonce", "хмара": "khmara", "будинок": "budynok",
        "дерево": "derevo", "підпис": "pidpys"}


def _canvas():
    im = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def _box(*v):
    return [int(round(x * K)) for x in v]


def _part(name, caption="Мій дім"):
    im, d = _canvas()
    if name == "небо":
        d.rectangle(_box(0, 0, W, H), fill="#BFD8F5")
    elif name == "трава":
        d.rectangle(_box(0, 600, W, H), fill="#7FB07A")
    elif name == "сонце":
        d.ellipse(_box(870, 80, 1050, 260), fill="#F7CE46")
    elif name == "хмара":
        for cx, cy, rx, ry in [(800, 255, 95, 48), (880, 225, 80, 55), (960, 260, 90, 45), (870, 275, 120, 38)]:
            d.ellipse(_box(cx - rx, cy - ry, cx + rx, cy + ry), fill="#FFFFFF")
    elif name == "будинок":
        d.rectangle(_box(480, 430, 760, 660), fill="#C98A4B")
        d.polygon(_box(450, 432, 790, 432, 620, 300), fill="#D9342B")
        d.rectangle(_box(520, 480, 592, 552), fill="#8EC5F0")
        d.rectangle(_box(640, 555, 704, 660), fill="#6E4426")
    elif name == "дерево":
        d.rectangle(_box(326, 470, 374, 690), fill="#7A5230")
        for cx, cy, r in [(350, 400, 105), (280, 450, 70), (420, 450, 70)]:
            d.ellipse(_box(cx - r, cy - r, cx + r, cy + r), fill="#4E8F4A")
    elif name == "підпис":
        f = ImageFont.truetype(BOLD, 72 * K)
        d.text(_box(60, 770), caption, font=f, fill="#FFFFFF")
    return im.resize((W, H), Image.LANCZOS)


def land_layers():
    """{назва шару: шлях до PNG} для краєвиду; порядок — LAND (знизу вгору)."""
    os.makedirs(ASSETS, exist_ok=True)
    out = {}
    for n in LAND:
        p = os.path.join(ASSETS, f"shar_{SLUG[n]}.png")
        if not os.path.exists(p):
            _part(n).save(p)
        out[n] = p
    return out


def land_flat(order=None, opacity=None, hidden=()):
    """Склеєний краєвид (як PNG після експорту) — для ілюстрацій на слайдах."""
    paths = land_layers()
    base = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    for n in (order or LAND):
        if n in hidden:
            continue
        im = Image.open(paths[n])
        if opacity and n in opacity:
            a = im.getchannel("A").point(lambda v: int(v * opacity[n] / 100))
            im.putalpha(a)
        base.alpha_composite(im)
    return base.convert("RGB")


def land_steps(order=None, hidden=(), opacity=None, active=None, zoom=1.3):
    """Кроки сценарію kritashot: документ 1200 × 900 і сім шарів краєвиду."""
    paths = land_layers()
    st = [{"new": [W, H, "Краєвид — Прізвище"]}, {"drop_bg": True}]
    for n in (order or LAND):
        st.append({"png_layer": [n, paths[n]]})
    for n, v in (opacity or {}).items():
        st.append({"opacity": [n, v]})
    for n in hidden:
        st.append({"hide": n})
    st += [{"zoom": zoom}, {"active": active or (order or LAND)[-1]}]
    return st


def doc_rect(zoom, w=W, h=H, pad=4):
    """Де на екрані Krita (у точках) лежить документ w × h при масштабі zoom (скрін kritashot scale=2)."""
    cx, cy = 579, 405
    ww, hh = w * zoom / 2, h * zoom / 2
    return (int(cx - ww / 2) - pad, int(cy - hh / 2) - pad, int(cx + ww / 2) + pad, int(cy + hh / 2) + pad)


# ---------------- плакат до змагань (урок І-15) ----------------
PW, PH = 2000, 1400
POSTER = ["фон", "м’яч", "деталі"]              # растрові шари знизу вгору; підкладка й текст — векторні
POSTER_SLUG = {"фон": "fon", "м’яч": "miach", "деталі": "detali"}
INTER_THIN = "/usr/share/fonts/opentype/inter/Inter-Thin.otf"


def _poster_part(name):
    im = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if name == "фон":
        for y in range(PH):                      # м’який градієнт: світло-блакитний → світло-зелений
            t = y / PH
            col = (int(214 + (196 - 214) * t), int(234 + (232 - 234) * t), int(250 + (206 - 250) * t), 255)
            d.line((0, y, PW, y), fill=col)
    elif name == "м’яч":                         # великий баскетбольний м’яч — головний об’єкт
        cx, cy, r = 1000, 820, 420
        ball = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
        b = ImageDraw.Draw(ball)
        b.ellipse((cx - r, cy - r, cx + r, cy + r), fill="#E8772E")
        b.line((cx - r, cy, cx + r, cy), fill="#3A2A20", width=14)
        b.line((cx, cy - r, cx, cy + r), fill="#3A2A20", width=14)
        b.arc((cx - r - 260, cy - r, cx - 120, cy + r), -60, 60, fill="#3A2A20", width=14)
        b.arc((cx + 120, cy - r, cx + r + 260, cy + r), 120, 240, fill="#3A2A20", width=14)
        mask = Image.new("L", (PW, PH), 0)
        ImageDraw.Draw(mask).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
        im.paste(ball, (0, 0), mask)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline="#3A2A20", width=14)
    elif name == "деталі":                       # зірочки-конфеті
        import math
        for cx, cy, r, col in [(260, 620, 40, "#F7CE46"), (1760, 560, 46, "#F7CE46"), (380, 1180, 30, "#D9342B"),
                               (1640, 1200, 34, "#2F6FB7"), (200, 900, 24, "#2F6FB7"), (1820, 900, 26, "#D9342B")]:
            pts = []
            for k in range(10):
                a = -math.pi / 2 + k * math.pi / 5
                rr = r if k % 2 == 0 else r * 0.45
                pts += [cx + rr * math.cos(a), cy + rr * math.sin(a)]
            d.polygon(pts, fill=col)
    return im


def poster_layers():
    os.makedirs(ASSETS, exist_ok=True)
    out = {}
    for n in POSTER:
        p = os.path.join(ASSETS, f"plakat_{POSTER_SLUG[n]}.png")
        if not os.path.exists(p):
            _poster_part(n).save(p)
        out[n] = p
    return out


def poster_svg(part):
    head = f'<svg xmlns="http://www.w3.org/2000/svg" width="{PW}" height="{PH}" viewBox="0 0 {PW} {PH}">'
    if part == "підкладка":
        body = '<rect x="330" y="70" width="1340" height="320" rx="40" fill="#1F2A44" fill-opacity="0.72"/>'
    elif part == "заголовок":
        body = ('<text x="1000" y="250" text-anchor="middle" style="font-family:DejaVu Sans;font-weight:bold;'
                'font-size:190px;fill:#FFFFFF">Змагання</text>')
    else:  # дата
        body = ('<text x="1000" y="345" text-anchor="middle" style="font-family:DejaVu Sans;font-weight:bold;'
                'font-size:70px;fill:#F7CE46">18 жовтня · спортзал</text>')
    return head + body + "</svg>"


def poster_steps(zoom=0.42, active="дата", opacity=None, upto=None):
    """Плакат 2000 × 1400: фон, м’яч, деталі (растр) + підкладка, заголовок, дата (вектор)."""
    paths = poster_layers()
    st = [{"new": [PW, PH, "Плакат — Прізвище"]}, {"hide_docker": "PresetDocker"}, {"drop_bg": True}]
    order = POSTER + ["підкладка", "заголовок", "дата"]
    for n in order[:order.index(upto) + 1 if upto else None]:
        if n in paths:
            st.append({"png_layer": [n, paths[n]]})
        else:
            st.append({"svg": poster_svg(n), "name": n})
    for n, v in (opacity or {}).items():
        st.append({"opacity": [n, v]})
    st += [{"zoom": zoom}, {"active": active}]
    return st


def poster_flat():
    """Готовий плакат як PNG (для слайдів): растрові шари + той самий вектор, намальований PIL."""
    base = Image.new("RGBA", (PW, PH), (255, 255, 255, 255))
    for p in poster_layers().values():
        base.alpha_composite(Image.open(p))
    d = ImageDraw.Draw(base, "RGBA")
    d.rounded_rectangle((330, 70, 1670, 390), 40, fill=(31, 42, 68, 184))
    f1 = ImageFont.truetype(BOLD, 190)
    f2 = ImageFont.truetype(BOLD, 70)
    d.text((1000, 250), "Змагання", font=f1, fill="#FFFFFF", anchor="ms")
    d.text((1000, 345), "18 жовтня · спортзал", font=f2, fill="#F7CE46", anchor="ms")
    return base.convert("RGB")


def poster_patient(w=1000):
    """Плакат-пацієнт: розтягнутий фон-трава, світло-зелений тонкий заголовок, три шрифти, вісім однакових м’ячів,
    логотип у білому прямокутнику."""
    import random
    rnd = random.Random(7)
    small = Image.new("RGB", (30, 20))
    for x in range(30):
        for y in range(20):
            g = rnd.randint(110, 170)
            small.putpixel((x, y), (int(g * 0.45), g, int(g * 0.35)))
    h = int(w * 0.7)
    im = small.resize((w, h), Image.NEAREST).convert("RGBA")
    d = ImageDraw.Draw(im, "RGBA")
    k = w / 1000
    for cx, cy in [(120, 140), (330, 120), (560, 150), (820, 130), (160, 420), (420, 470), (680, 430), (880, 520)]:
        r = 62 * k
        cx, cy = cx * k, cy * k
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill="#E8772E", outline="#3A2A20", width=int(4 * k))
        d.line((cx - r, cy, cx + r, cy), fill="#3A2A20", width=int(4 * k))
        d.line((cx, cy - r, cx, cy + r), fill="#3A2A20", width=int(4 * k))
    d.text((w / 2, h * 0.47), "Змагання", font=ImageFont.truetype(INTER_THIN, int(90 * k)), fill="#B9E6A8", anchor="mm")
    d.text((w - 18 * k, h - 64 * k), "18 жовтня", font=ImageFont.truetype("/usr/share/fonts/truetype/baskerville/GFSBaskerville.otf",
                                                                       int(34 * k)), fill="#7CC36A", anchor="rs")
    d.text((w - 18 * k, h - 26 * k), "спортзал", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
                                                                      int(24 * k)), fill="#D9342B", anchor="rs")
    d.rectangle((24 * k, h - 120 * k, 130 * k, h - 24 * k), fill="#FFFFFF")
    d.ellipse((44 * k, h - 100 * k, 110 * k, h - 44 * k), fill="#2F6FB7")
    d.text((77 * k, h - 72 * k), "36", font=ImageFont.truetype(BOLD, int(24 * k)), fill="#FFFFFF", anchor="mm")
    return im.convert("RGB")
