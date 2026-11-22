"""Додатки до колод 6 класу (Krita, уроки І-11…І-15): готові зразки виконаних завдань — справжні файли Krita.

Кожен зразок збирає справжня Krita під Xvfb (kritashot.kshot(..., save=[...])): створює документ, кладе шари
(растрові — з малюнків grafika6/shary6, векторні — з SVG, тож у .kra вони лишаються фігурами), а коло-заливку й
мазки пензля робить мишкою (xdotool), і сама зберігає робочий .kra та експортує PNG.
Учитель відкриває файл у Krita й показує учням, яким має бути результат.

Запуск: python3 Tools/slides/krita_dodatky6.py [І-12 …] — без аргументів робить усі уроки.
Файли: «Презентації уроків/6 клас/Додатки/Урок І-xx. …/Зразок — ….kra | .png»."""
import os
import sys

from PIL import Image, ImageDraw

from deck import REPO
import grafika6 as g
import shary6 as h
from kritashot import kshot

OUT = os.path.join(REPO, "Презентації уроків", "6 клас", "Додатки")
LESSON = {
    "І-11": "Урок І-11. Растрова та векторна графіка",
    "І-12": "Урок І-12. Растрові зображення в Krita",
    "І-13": "Урок І-13. Векторні зображення в Krita",
    "І-14": "Урок І-14. Шари в Krita",
    "І-15": "Урок І-15. Текст у зображеннях. Підсумок",
}
AWAY = "mousemove 1300 740"


def make(lesson, name, steps, xdo=None):
    """Справжня Krita виконує кроки (і мишку), потім зберігає «Зразок — name».kra і .png."""
    d = os.path.join(OUT, LESSON[lesson])
    os.makedirs(d, exist_ok=True)
    base = os.path.join(d, f"Зразок — {name}")
    for ext in (".kra", ".png"):
        if os.path.exists(base + ext):
            os.remove(base + ext)
    kshot(steps, (xdo or []) + [AWAY], save=[{"save_kra": base + ".kra"}, {"export_png": base + ".png"}])
    ok = os.path.exists(base + ".kra") and os.path.exists(base + ".png")
    print(("✓ " if ok else "✗ ") + base)
    return base


def pixel_art(rows, colors, name):
    """Піксель-арт 1:1 (рядки символів → пікселі), прозоре тло."""
    hgt, w = len(rows), len(rows[0])
    im = Image.new("RGBA", (w, hgt), (0, 0, 0, 0))
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in colors:
                im.putpixel((x, y), colors[ch])
    p = g.path(name)
    im.save(p)
    return p


SMILE16 = ["................",
           ".....######.....",
           "...##YYYYYY##...",
           "..#YYYYYYYYYY#..",
           ".#YYYYYYYYYYYY#.",
           ".#YYYKYYYYKYYY#.",
           "#YYYYKYYYYKYYYY#",
           "#YYYYYYYYYYYYYY#",
           "#YYYYYYYYYYYYYY#",
           "#YYPYYYYYYYYPYY#",
           "#YYYKYYYYYYKYYY#",
           ".#YYYKKKKKKYYY#.",
           ".#YYYYYYYYYYYY#.",
           "..#YYYYYYYYYY#..",
           "...##YYYYYY##...",
           ".....######....."]
CAT16 = ["................",
         "..#..........#..",
         "..##........##..",
         "..#O#......#O#..",
         "..#OO######OO#..",
         "..#OOOOOOOOOO#..",
         ".#OOGOOOOOOGOO#.",
         ".#OOGOOOOOOGOO#.",
         ".#OOOOOPPOOOOO#.",
         ".#OOOOOOOOOOOO#.",
         "..#OOO#OO#OOO#..",
         "...##OOOOOO##...",
         "....#OOOOOO#....",
         "...#OO#OO#OO#...",
         "...##########...",
         "................"]
PX = {"#": (47, 48, 51, 255), "Y": (247, 206, 70, 255), "K": (47, 48, 51, 255), "P": (242, 140, 150, 255),
      "O": (232, 136, 54, 255), "G": (78, 143, 74, 255)}


def new_with(w, hgt, title, layers, bg=True):
    """Новий документ і растрові шари з картинок [(назва, шлях)]."""
    st = [{"new": [w, hgt, title] + ([] if bg else ["transparent"])}]
    if not bg:
        st.append({"drop_bg": True})
    st += [{"png_layer": [n, p]} for n, p in layers]
    return st + [{"zoom": 1.0}]


def full(w, hgt, src, name):
    """Картинку src (меншу) кладемо на прозорий аркуш w × hgt у ту саму точку — для png_layer."""
    im = Image.new("RGBA", (w, hgt), (0, 0, 0, 0))
    im.alpha_composite(Image.open(src).convert("RGBA"))
    p = g.path(name)
    im.save(p)
    return p


# ---------------------------------------------------------------- І-11
def i11():
    heart = g.pixel_heart()                         # 8 × 8, біле тло, червоне сердечко за диктантом
    make("І-11", "піксельне сердечко 8 × 8", new_with(8, 8, "Сердечко", [("сердечко", heart)], bg=False))

    make("І-11", "смайлик 16 × 16 (рівень 2)",
         new_with(16, 16, "Смайлик", [("смайлик", pixel_art(SMILE16, PX, "pix_smile16.png"))], bg=False))
    make("І-11", "піксельний кіт 16 × 16 (рівень 3)",
         new_with(16, 16, "Кіт", [("кіт", pixel_art(CAT16, PX, "pix_cat16.png"))], bg=False))
    # 8 × 8 і 16 × 16 на проєкторі — крихітні; поруч збільшена копія для показу (піксель → квадрат)
    d = os.path.join(OUT, LESSON["І-11"])
    for n in ("піксельне сердечко 8 × 8", "смайлик 16 × 16 (рівень 2)", "піксельний кіт 16 × 16 (рівень 3)"):
        im = Image.open(os.path.join(d, f"Зразок — {n}.png"))
        k = 480 // im.width
        im.resize((im.width * k, im.height * k), Image.NEAREST).save(os.path.join(d, f"Зразок — {n} — збільшено.png"))


# ---------------------------------------------------------------- І-12
def i12():
    # жовте коло: справжнє еліптичне виділення мишкою + заливка, тло прозоре (як у «Зроби зараз»)
    x0, y0, x1, y1 = g.scr(40, 40) + g.scr(460, 460)
    cx, cy = g.scr(250, 250)
    drag = [f"mousemove {x0} {y0}", "mousedown 1", f"mousemove {(x0 + x1) // 2} {(y0 + y1) // 2}",
            f"mousemove {x1} {y1}", "mouseup 1", "sleep 0.5"]
    make("І-12", "жовте коло",
         [{"new": [500, 500, "Емодзі", "transparent"]}, {"drop_bg": True}, {"layer": "коло"}, {"zoom": 1.0}, {"fg": "#F7CE46"},
          {"tool": "KisToolSelectElliptical"}],
         drag + ["key f", "sleep 0.5", f"mousemove {cx} {cy}", "click 1", "sleep 1.5", "key ctrl+shift+a", "sleep 0.5"])
    make("І-12", "емодзі (рівень 1)", new_with(500, 500, "Емодзі", [("емодзі", g.save_emoji(4, 500))], bg=False))
    make("І-12", "сумне емодзі (рівень 2)",
         new_with(500, 500, "Сумне емодзі", [("емодзі", g.save_emoji(4, 500, "emodzi_sad.png", mood="sad"))], bg=False))
    # рівень 3 — наліпка: персонаж на прозорому тлі
    k = 4
    im = Image.new("RGBA", (500 * k, 500 * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = lambda *v: [x * k for x in v]  # noqa: E731
    d.rectangle(s(205, 260, 295, 430), fill="#F4E7D0", outline="#8A6B4A", width=6 * k)          # ніжка гриба
    d.pieslice(s(80, 90, 420, 400), 180, 360, fill="#D9342B", outline="#7A1E18", width=6 * k)   # капелюх
    for cx_, cy_, r in [(170, 180, 26), (250, 140, 30), (330, 185, 24), (215, 215, 16), (300, 225, 15)]:
        d.ellipse(s(cx_ - r, cy_ - r, cx_ + r, cy_ + r), fill="#FFFFFF")
    for ex in (230, 270):
        d.ellipse(s(ex - 8, 320, ex + 8, 342), fill="#2F3033")
    d.arc(s(225, 330, 275, 370), 20, 160, fill="#2F3033", width=5 * k)
    p = g.path("nalipka_hryb.png")
    im.resize((500, 500), Image.LANCZOS).save(p)
    make("І-12", "наліпка-грибок (рівень 3)", new_with(500, 500, "Наліпка", [("грибок", p)], bg=False))


# ---------------------------------------------------------------- І-13
CIRCLES_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500">'
               '<circle cx="130" cy="130" r="90" fill="#F7CE46" stroke="none"/>'
               '<circle cx="370" cy="130" r="90" fill="none" stroke="#2F3033" stroke-width="2"/>'
               '<circle cx="130" cy="370" r="90" fill="#FFFFFF" stroke="#D9342B" stroke-width="10"/>'
               '<circle cx="370" cy="370" r="90" fill="#2F6FB7" stroke="#F7CE46" stroke-width="6"/></svg>')
ROBOT_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500">'
             '<rect x="240" y="40" width="20" height="50" fill="#8C8F94" stroke="#2F3033" stroke-width="3"/>'
             '<circle cx="250" cy="38" r="16" fill="#D9342B" stroke="#2F3033" stroke-width="3"/>'
             '<rect x="150" y="90" width="200" height="140" rx="20" fill="#9CC3E6" stroke="#2F3033" stroke-width="4"/>'
             '<circle cx="205" cy="150" r="22" fill="#FFFFFF" stroke="#2F3033" stroke-width="3"/>'
             '<circle cx="295" cy="150" r="22" fill="#FFFFFF" stroke="#2F3033" stroke-width="3"/>'
             '<rect x="210" y="195" width="80" height="14" rx="7" fill="#2F3033"/>'
             '<rect x="120" y="245" width="260" height="170" rx="16" fill="#F7CE46" stroke="#2F3033" stroke-width="4"/>'
             '<polygon points="250,280 280,330 250,380 220,330" fill="#D9342B" stroke="#2F3033" stroke-width="3"/>'
             '<rect x="150" y="415" width="60" height="60" fill="#8C8F94" stroke="#2F3033" stroke-width="4"/>'
             '<rect x="290" y="415" width="60" height="60" fill="#8C8F94" stroke="#2F3033" stroke-width="4"/></svg>')


def vec(title, svg, name="фігури"):
    return [{"new": [500, 500, title]}, {"svg": svg, "name": name}, {"zoom": 1.0}]


def i13():
    make("І-13", "будиночок із трьох фігур", vec("Будиночок", g.HOUSE_SVG, "будиночок"))
    make("І-13", "одне коло — чотири вигляди", vec("Чотири кола", CIRCLES_SVG, "кола"))
    make("І-13", "ракета за описом", vec("Ракета", g.ROCKET_SVG, "ракета"))
    make("І-13", "робот із фігур (рівень 3)", vec("Робот", ROBOT_SVG, "робот"))


# ---------------------------------------------------------------- І-14
CARD = ["фон", "сніг", "ялинка", "сніжинки", "напис"]


def card_layers():
    W, H = 1200, 900
    out = {}
    for n in CARD:
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if n == "фон":
            for y in range(H):
                t = y / H
                d.line((0, y, W, y), fill=(int(20 + 30 * t), int(32 + 50 * t), int(78 + 60 * t), 255))
        elif n == "сніг":
            d.ellipse((-200, 640, 1400, 1300), fill="#F2F6FB")
        elif n == "ялинка":
            d.rectangle((575, 640, 625, 720), fill="#6E4426")
            for k, (top, half) in enumerate([(250, 110), (360, 160), (470, 210)]):
                d.polygon([(600, top), (600 - half, top + 190), (600 + half, top + 190)], fill="#2E7D4F")
            d.polygon([(600, 205), (614, 240), (652, 240), (621, 262), (633, 298), (600, 276), (567, 298), (579, 262),
                       (548, 240), (586, 240)], fill="#F7CE46")
        elif n == "сніжинки":
            import random
            rnd = random.Random(5)
            for _ in range(70):
                x, y, r = rnd.randint(0, W), rnd.randint(0, 640), rnd.randint(3, 8)
                d.ellipse((x - r, y - r, x + r, y + r), fill="#FFFFFF")
        elif n == "напис":
            from PIL import ImageFont
            f = ImageFont.truetype(h.BOLD, 96)
            d.text((W // 2, 120), "З Новим роком!", font=f, fill="#F7CE46", anchor="mm", stroke_width=4,
                   stroke_fill="#1F2A44")
        p = g.path(f"lystivka_{CARD.index(n)}.png")
        im.save(p)
        out[n] = p
    return out


def i14():
    names = h.LAND
    empty = [{"new": [1200, 900, "Краєвид — Прізвище", "transparent"]}, {"drop_bg": True}]
    for n in names:
        empty.append({"layer": n})
    make("І-14", "сім порожніх шарів із назвами", empty + [{"zoom": 0.6}])

    land = h.land_steps(zoom=0.6)
    make("І-14", "краєвид «Мій дім» — кожне на своєму шарі", land)
    make("І-14", "краєвид, хмара 50 % (прозорість)", h.land_steps(zoom=0.6, opacity={"хмара": 50}))
    bad = names[:]
    bad.remove("трава")
    bad.append("трава")
    make("І-14", "помилка — трава на верху стопки", h.land_steps(order=bad, zoom=0.6, active="трава"))
    cl = card_layers()
    st = [{"new": [1200, 900, "Листівка"]}, {"drop_bg": True}] + [{"png_layer": [n, cl[n]]} for n in CARD]
    st += [{"opacity": ["сніжинки", 70]}, {"zoom": 0.6}]
    make("І-14", "листівка з п’яти шарів (рівень 3)", st)


# ---------------------------------------------------------------- І-15
TITLE_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900">'
             '<text x="60" y="842" style="font-family:DejaVu Sans;font-weight:bold;font-size:90px;fill:#FFFFFF">'
             'Мій дім</text></svg>')


def i15():
    st = h.land_steps(order=[n for n in h.LAND if n != "підпис"], zoom=0.6)
    st.insert(-2, {"svg": TITLE_SVG, "name": "підпис"})
    make("І-15", "напис «Мій дім» на окремому шарі", st)
    make("І-15", "плакат до змагань (Завдання 2)", h.poster_steps(zoom=0.4))
    p = g.path("plakat_pacient_full.png")
    h.poster_patient(2000).save(p)
    make("І-15", "плакат-пацієнт (для діагнозу)", new_with(2000, 1400, "Плакат-пацієнт", [("плакат", p)], bg=False)
         [:-1] + [{"zoom": 0.4}])


ALL = {"І-11": i11, "І-12": i12, "І-13": i13, "І-14": i14, "І-15": i15}

if __name__ == "__main__":
    for k in (sys.argv[1:] or ALL):
        ALL[k]()


def zrazky_slide(d, lesson, notes=""):
    """Слайд «Готові зразки»: мініатюри PNG із «Додатків» і назви файлів (.kra відкривається в Krita з усіма шарами).
    Ставимо перед «Як оцінюємо». Якщо зразків ще не зроблено — слайда немає."""
    import glob
    from deck import data_uri, INK2
    folder = os.path.join(OUT, LESSON[lesson])
    pngs = [p for p in sorted(glob.glob(os.path.join(folder, "Зразок — *.png"))) if "збільшено" not in p and "порожніх" not in p]
    if not pngs:
        return None
    s = d.slide("Готові зразки",
                (notes or "Готові файли, зроблені в Krita, — у сховищі: «Презентації уроків/6 клас/Додатки/"
                 + LESSON[lesson] + "». Відкрийте .kra у Krita (Файл → Відкрити) — видно всі шари, можна показати, "
                 "як зроблено. PNG — просто картинка результату.\nПоказуємо зразок перед самостійною роботою або "
                 "наприкінці для самоперевірки."))
    s.h2("Готові зразки")
    s.sub("Файли — у папці <b>Додатки / " + LESSON[lesson] + "</b>: .kra (з шарами) і .png")
    n = len(pngs)
    cols = min(n, 4 if n > 3 else n)
    rows = (n + cols - 1) // cols
    cw = (1664 - 40 * (cols - 1)) // cols
    chh = (700 - 30 * (rows - 1)) // rows
    for i, p in enumerate(pngs[:8]):
        x = 128 + (i % cols) * (cw + 40)
        y = 290 + (i // cols) * (chh + 30)
        big = p[:-4] + " — збільшено.png"
        src = big if os.path.exists(big) else p
        ih = chh - 70
        pix = "image-rendering:pixelated;" if os.path.exists(big) else ""
        s.raw(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{cw}px;height:{ih}px;'
              f'background:repeating-conic-gradient(#e6e8ec 0% 25%, #fff 0% 50%) 50%/24px 24px;'
              f'border:2px solid #2F3033;border-radius:10px;overflow:hidden;box-sizing:border-box;display:flex;'
              f'align-items:center;justify-content:center"><img alt="" src="{data_uri(src)}" '
              f'style="max-width:100%;max-height:100%;{pix}"></div>')
        name = os.path.basename(p)[len("Зразок — "):-4]
        s.text(x, y + ih + 8, cw, 60, name, size=22 if cols > 3 else 25, color=INK2, align="center", lh=1.15)
    return s
