"""Генератор HTML-презентацій у стилі наявних «Презентацій уроків».

Бере рушій слайдів (стилі, шрифти, скрипт показу) з уже готової презентації
й складає нові слайди з тих самих будівельних блоків: заголовок, блок коду,
«ЕКРАН», картки, таблиці, нумеровані завдання, анімовані появи по кліку.

Використання — див. скрипти поруч (urok10.py тощо): кожен будує одну колоду
й зберігає її через Deck.save().
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
ENGINE_SOURCE = os.path.join(REPO, "Презентації уроків", "Python", "Урок 11. Цикл for і range.html")

MONO = "'Roboto Mono', 'Courier New', monospace"
INK = "#2F3033"
INK2 = "#45484D"
LIGHT_BG = "#D5DBE3"
DARK_BG = "#3E3F42"
PAPER = "#EEF1F5"
MUTED_ON_DARK = "#BFC6D0"
BLUE = "#2F6FB7"
BLUE_ON_DARK = "#A8CBF3"
ORANGE = "#B85F1E"
PEACH_ON_DARK = "#F2C38F"

ICON = {  # гліфи шрифту mc-anthropicons, який уже вбудований у рушій
    "code": "", "book": "", "play": "", "wrench": "",
    "clock": "", "star": "", "chart": "", "warning": "",
    "bulb": "", "lock": "", "key": "", "search": "",
    "check": "", "edit": "", "image": "", "file": "",
    "list": "", "keyboard": "", "users": "", "eye": "",
    "computer": "", "tasks": "", "branch": "", "reload": "",
    "globe": "", "lightning": "", "temp": "", "trash": "",
    "sort": "", "filter": "", "home": "", "help": "",
}

# Пари «плям» на тлі — ті самі, що в наявних колодах.
LIGHT_BLOBS = [
    [(0, 180, 900, 800, "40% 50%", 68), ("rot", 1380, 0, 520, 400, 18)],
    [(900, 0, 1020, 520, "50% 30%", 70), ("rot", 520, 700, 520, 360, 24)],
    [(0, 0, 1100, 620, "35% 30%", 68), ("rot", 1300, 600, 620, 480, 20)],
    [(1000, 380, 920, 700, "60% 60%", 68), ("rot", 40, 40, 560, 360, -16)],
    [(0, 400, 900, 680, "40% 60%", 68), (1100, 0, 820, 600, "60% 35%", 70)],
]
DARK_BLOBS = [
    [(0, 500, 900, 580, "30% 70%")],
    [(1000, 0, 920, 620, "60% 30%")],
]


def esc(s):
    return html.escape(s, quote=True)


def c(code, dark=False):
    """Код у рядку тексту: моноширинний синій."""
    col = BLUE_ON_DARK if dark else BLUE
    return f'<span style="font-family:{MONO};font-weight:600;color:{col}">{esc(code)}</span>'


def _blob_html(spec, dark):
    out = []
    for b in spec:
        if b[0] == "rot":
            _, x, y, w, h, r = b
            out.append(
                f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
                f'border-radius:180px;background:linear-gradient(135deg, rgba(172,203,243,0.8) 0%, '
                f'rgba(213,219,227,0) 75%);transform:rotate({r}deg);filter:blur(6px)"></div>')
        elif dark:
            x, y, w, h, at = b
            out.append(
                f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
                f'border-radius:50%;background:radial-gradient(ellipse at {at}, rgba(156,192,239,0.35) 0%, '
                f'rgba(62,63,66,0) 70%)"></div>')
        else:
            x, y, w, h, at, stop = b
            out.append(
                f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
                f'border-radius:50%;background:radial-gradient(ellipse at {at}, #9CC0EF 0%, '
                f'rgba(213,219,227,0) {stop}%)"></div>')
    return "".join(out)


class Slide:
    def __init__(self, deck, index, label, notes, dark, blobs, header):
        self.deck = deck
        self.index = index
        self.label = label
        self.notes = notes
        self.dark = dark
        self.parts = []
        self.frames = []          # [(effect)]
        self._target = self.parts
        pool = DARK_BLOBS if dark else LIGHT_BLOBS
        if isinstance(blobs, list):
            spec = blobs
        else:
            spec = pool[(index if blobs is None else blobs) % len(pool)]
        self.parts.append(_blob_html(spec, dark))
        if header:
            self.header()

    # ---- службове ----
    def add(self, s):
        self._target.append(s)
        return self

    def frame(self, effect="rise"):
        """with s.frame(): … — усе всередині з'явиться окремим кліком."""
        slide = self

        class _F:
            def __enter__(self_):
                slide._saved = slide._target
                slide._buf = []
                slide._target = slide._buf
                return slide

            def __exit__(self_, *a):
                k = len(slide.frames)
                fid = f"f{slide.index + 1}-{k}"
                slide.frames.append((fid, effect))
                slide._target = slide._saved
                slide._target.append(
                    f'<div data-frame-id="{fid}" style="position:absolute;left:0px;top:0px;'
                    f'width:1920px;height:1080px;">' + "".join(slide._buf) + "</div>")
        return _F()

    @property
    def ink(self):
        return PAPER if self.dark else INK

    @property
    def ink2(self):
        return MUTED_ON_DARK if self.dark else INK2

    # ---- шапка ----
    def header(self, text=None):
        text = text or self.deck.header_text
        col = self.ink
        self.add(
            f'<div style="position:absolute;left:128px;top:56px;width:900px;display:flex;flex-direction:row;'
            f'align-items:center;gap:16px"><svg preserveaspectratio="xMidYMid meet" style="width:40px;'
            f'height:40px;display:block" viewbox="0 0 100 100"><text dominant-baseline="central" fill="{col}" '
            f'font-family="mc-anthropicons" font-size="90" text-anchor="middle" text-rendering="geometricPrecision" '
            f'x="50" y="54">{ICON[self.deck.header_icon]}</text></svg><p style="font-size:28px;font-weight:600;'
            f'line-height:1.4;color:{col}">{esc(text)}</p></div>')

    def topic_corner(self, topic):
        self.add(
            f'<div style="position:absolute;left:1192px;top:52px;width:600px;height:70px;display:flex;'
            f'flex-direction:column;justify-content:flex-start;gap:0px;"><p style="font-size:24px;font-weight:400;'
            f'line-height:1.35;color:{INK2};text-align:right">Тема уроку:</p><p style="font-size:24px;'
            f'font-weight:400;line-height:1.35;color:{INK2};text-align:right"><b>{esc(topic)}</b></p></div>'
            f'<div style="position:absolute;left:128px;top:124px;width:1664px;height:2px;background:{INK};'
            f'border-radius:0px;box-sizing:border-box"></div>')

    # ---- текст ----
    def h2(self, text, size=76, top=110, width=1664, left=128):
        ls = -2 if size >= 64 else -1
        self.add(
            f'<h2 style="position:absolute;left:{left}px;top:{top}px;width:{width}px;font-size:{size}px;'
            f'font-weight:700;line-height:1.1;color:{self.ink};letter-spacing:{ls}px;">{text}</h2>')

    def sub(self, text, top=214, size=36, left=128, width=1664):
        self.text(left, top, width, 60, text, size=size, color=self.ink2, lh=1.4)

    def text(self, x, y, w, h, body, size=32, weight=400, color=None, align="left", lh=1.3,
             valign="flex-start", mono=False, extra=""):
        color = color or self.ink
        al = "" if align == "left" else f";text-align:{align}"
        ff = f";font-family:{MONO}" if mono else ""
        hh = f"height:{h}px;" if h else ""
        paras = body if isinstance(body, list) else [body]
        ps = "".join(
            f'<p style="font-size:{size}px;font-weight:{weight};line-height:{lh};color:{color}{al}{ff}{extra}">{p}</p>'
            for p in paras)
        gap = 12 if len(paras) > 1 else 0
        self.add(
            f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;{hh}display:flex;'
            f'flex-direction:column;justify-content:{valign};gap:{gap}px;">{ps}</div>')

    def note(self, y, body, size=32, weight=600):
        """Підсумковий рядок по центру внизу."""
        self.text(128, y, 1664, 120, body, size=size, weight=weight, align="center")

    # ---- прямокутники ----
    def box(self, x, y, w, h, kind="light", radius=20):
        bg = {
            "light": "background:rgba(238,241,245,0.55)",
            "light2": "background:rgba(238,241,245,0.4)",
            "blue": "background:linear-gradient(120deg, #A9CBF3 0%, #E3EEFB 100%)",
            "orange": "background:linear-gradient(120deg, #F6C795 0%, #FBE8D3 100%)",
            "dark": f"background:{DARK_BG}",
            "screen": "background:#2A2B2E",
            "darkcard": f"background:{INK}",
        }[kind]
        border = {
            "screen": "border:2px solid #6A6E75",
            "dark": "",
            "darkcard": f"border:2px solid {BLUE_ON_DARK}",
        }.get(kind, f"border:2px solid {DARK_BG}")
        self.add(
            f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;{bg};'
            f'border-radius:{radius}px;box-sizing:border-box;{border}"></div>')

    def card(self, x, y, w, h, title=None, body=None, kind="light", title_size=34, body_size=28,
             title_color=None, pad=32, valign="center", align="left"):
        self.box(x, y, w, h, kind)
        dark_kind = kind in ("dark", "screen", "darkcard")
        tc = title_color or (PEACH_ON_DARK if kind == "darkcard" else (PAPER if dark_kind else INK))
        bc = PAPER if dark_kind else INK2
        al = "" if align == "left" else f";text-align:{align}"
        ps = []
        if title:
            ps.append(f'<p style="font-size:{title_size}px;font-weight:700;line-height:1.25;color:{tc}{al}">{title}</p>')
        if body:
            for b in (body if isinstance(body, list) else [body]):
                ps.append(f'<p style="font-size:{body_size}px;font-weight:400;line-height:1.35;color:{bc}{al}">{b}</p>')
        self.add(
            f'<div style="position:absolute;left:{x + pad}px;top:{y}px;width:{w - 2 * pad}px;height:{h}px;'
            f'display:flex;flex-direction:column;justify-content:{valign};gap:10px;'
            f'{"padding:26px 0px;box-sizing:border-box;" if valign != "center" else ""}">{"".join(ps)}</div>')

    def chip(self, x, y, w, h, body, kind="blue", size=40, mono=True, weight=800):
        self.box(x, y, w, h, kind, radius=16)
        col = PAPER if kind in ("dark", "screen") else INK
        self.text(x, y, w, h, body, size=size, weight=weight, align="center", lh=1.1,
                  valign="center", mono=mono, color=col)

    def code(self, x, y, w, h, code, size=30, framed=True, lh=1.55, color=PAPER):
        """Великий блок коду: світла рамка + темна вставка (як у наявних колодах)."""
        body = esc(code)
        if framed:
            self.add(
                f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
                f'background:rgba(238,241,245,0.4);border-radius:56px;box-sizing:border-box;'
                f'border:2px solid {DARK_BG}"></div>'
                f'<div style="position:absolute;left:{x + 14}px;top:{y + 14}px;width:{w - 28}px;height:{h - 28}px;'
                f'background:{DARK_BG};border-radius:44px;box-sizing:border-box"></div>')
            ix, iy, iw, ih = x + 58, y + 34, w - 116, h - 68
        else:
            self.box(x, y, w, h, "screen")
            ix, iy, iw, ih = x + 40, y + 20, w - 80, h - 40
        size = fit(code, iw, size)
        self.add(
            f'<div style="position:absolute;left:{ix}px;top:{iy}px;width:{iw}px;height:{ih}px;display:flex;'
            f'flex-direction:column;justify-content:center;"><p style="font-family:{MONO};font-size:{size}px;'
            f'line-height:{lh};color:{color};white-space:pre;">{body}</p></div>')

    def screen(self, x, y, w, h, out, label="ЕКРАН", size=30, valign="center"):
        """Темне «вікно виводу» з підписом ЕКРАН / ЗРАЗОК."""
        self.box(x, y, w, h, "screen")
        size = fit(out, w - 64, size)
        self.add(
            f'<div style="position:absolute;left:{x + 32}px;top:{y + 28}px;width:{w - 64}px;height:{h - 56}px;'
            f'display:flex;flex-direction:column;justify-content:{valign};gap:10px;">'
            f'<p style="font-size:24px;font-weight:700;line-height:1.4;color:{MUTED_ON_DARK};letter-spacing:2px">{esc(label)}</p>'
            f'<p style="font-family:{MONO};font-size:{size}px;line-height:1.45;color:{PAPER};white-space:pre;">{esc(out)}</p></div>')

    def mistake(self, x, y, w, code, fix, code_h=140, size=28):
        """Блок «типова помилка»: темний код угорі, пояснення під ним."""
        h = code_h + 110
        size = fit(code, w - 100, size)
        self.add(
            f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
            f'background:rgba(238,241,245,0.4);border-radius:28px;box-sizing:border-box;border:2px solid {DARK_BG}"></div>'
            f'<div style="position:absolute;left:{x + 14}px;top:{y + 14}px;width:{w - 28}px;height:{code_h}px;'
            f'background:{DARK_BG};border-radius:18px;box-sizing:border-box"></div>'
            f'<div style="position:absolute;left:{x + 50}px;top:{y + 14}px;width:{w - 100}px;height:{code_h}px;display:flex;'
            f'flex-direction:column;justify-content:center;"><p style="font-family:{MONO};font-size:{size}px;line-height:1.5;'
            f'color:{PAPER};white-space:pre;">{esc(code)}</p></div>')
        self.text(x + 32, y + code_h + 28, w - 64, 70, fix, size=28, weight=600, valign="center")

    # ---- нумерований список (завдання) ----
    def steps(self, items, x=128, y=206, w=700, size=33, gap=22, line_h=None):
        """Нумерований список завдань; висоту рядків рахує браузер, тож нічого не налазить."""
        rows = []
        for i, it in enumerate(items, 1):
            rows.append(
                f'<div style="display:flex;flex-direction:row;align-items:flex-start;gap:22px">'
                f'<div style="flex:none;width:48px;height:48px;border-radius:50%;background:{DARK_BG};display:flex;'
                f'flex-direction:column;align-items:center;justify-content:center"><p style="font-size:26px;'
                f'font-weight:700;line-height:1.2;color:{PAPER}">{i}</p></div>'
                f'<p style="flex:1;padding-top:2px;font-size:{size}px;font-weight:400;line-height:1.3;'
                f'color:{self.ink}">{it}</p></div>')
        self.add(
            f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;display:flex;flex-direction:column;'
            f'gap:{gap}px">' + "".join(rows) + "</div>")

    def pill(self, text):
        self.box(1432, 44, 360, 60, "light", radius=30)
        self.text(1432, 44, 360, 60, esc(text), size=26, weight=600, align="center", valign="center")

    # ---- таблиця ----
    def table(self, x, y, widths, rows, row_h=72, size=28, header=True, aligns=None, fills=None,
              head_bg=DARK_BG):
        cols = len(widths)
        aligns = aligns or ["left"] * cols
        fills = fills or {}
        lh = round(row_h / size, 3)
        cells = []
        for r, row in enumerate(rows):
            for ci, val in enumerate(row):
                last_c = ci == cols - 1
                last_r = r == len(rows) - 1
                br = "" if last_c else f"border-right:2px solid {DARK_BG};"
                bb = "" if last_r else f"border-bottom:2px solid {DARK_BG};"
                if header and r == 0:
                    style = f"font-weight:700;color:{PAPER};background:{head_bg};"
                else:
                    bg = fills.get((r, ci), fills.get((r, None), "rgba(238,241,245,0.7)"))
                    style = f"font-weight:400;color:{INK};background:{bg};"
                cells.append(
                    f'<p style="height:{row_h}px;padding:0px 20px;font-size:{size}px;line-height:{lh};'
                    f'text-align:{aligns[ci]};white-space:nowrap;overflow:hidden;{style}{br}{bb}">{val}</p>')
        tw = sum(widths) + 4
        th = row_h * len(rows) + 4
        tmpl = " ".join(f"{w}px" for w in widths)
        self.add(
            f'<div style="position:absolute;left:{x}px;top:{y}px;width:{tw}px;height:{th}px;display:grid;'
            f'grid-template-columns:{tmpl};border:2px solid {DARK_BG};border-radius:12px;overflow:hidden">'
            + "".join(cells) + "</div>")

    def stamp(self, x, y, w, text, rot=-7, size=56):
        self.add(
            f'<p style="position:absolute;left:{x}px;top:{y}px;width:{w}px;font-size:{size}px;font-weight:800;'
            f'line-height:1.2;color:{ORANGE};text-align:center;padding:10px 12px;border:5px solid {ORANGE};'
            f'border-radius:14px;background:rgba(238,241,245,0.92);letter-spacing:2px;text-transform:uppercase;'
            f'transform:rotate({rot}deg);">{text}</p>')

    def page(self, x, y, w, h, rows, margin=36, line_h=12, line_gap=14, bg="#FBFCFD", border=True,
             show_margins=False):
        """Мініатюра аркуша документа: рядки тексту — сірі смужки.
        rows: ("t", частка_ширини, вирівнювання) — заголовок; ("l", частка, вирівнювання[, відступ]) — рядок;
              ("gap", px) — порожнеча; ("txt", html, розмір, вирівнювання) — справжній текст."""
        bd = f"border:2px solid {DARK_BG};" if border else ""
        self.add(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{bg};'
                 f'border-radius:8px;box-sizing:border-box;{bd}box-shadow:0 10px 30px rgba(30,40,60,0.18)"></div>')
        if show_margins:
            self.add(f'<div style="position:absolute;left:{x + margin}px;top:{y + margin}px;width:{w - 2 * margin}px;'
                     f'height:{h - 2 * margin}px;border:2px dashed #9AA3AE;box-sizing:border-box"></div>')
        inner = w - 2 * margin
        cy = y + margin
        for r in rows:
            kind = r[0]
            if kind == "gap":
                cy += r[1]
                continue
            if kind == "txt":
                _, body, size, align = r
                self.text(x + margin, cy, inner, None, body, size=size, align=align, lh=1.3)
                cy += int(size * 1.3) + line_gap
                continue
            frac, align = r[1], r[2]
            indent = r[3] if len(r) > 3 else 0
            hh = line_h * 2 if kind == "t" else line_h
            col = "#4A4E55" if kind == "t" else "#AEB6C1"
            lw = int((inner - indent) * frac)
            if align == "center":
                lx = x + margin + (inner - lw) // 2
            elif align == "right":
                lx = x + margin + inner - lw
            else:
                lx = x + margin + indent
            self.add(f'<div style="position:absolute;left:{lx}px;top:{cy}px;width:{lw}px;height:{hh}px;'
                     f'border-radius:{hh // 2}px;background:{col}"></div>')
            cy += hh + line_gap
        return cy

    def raw(self, s):
        self.add(s)

    def icon_circle(self, x, y, icon, size=68, bg=DARK_BG, fg=BLUE_ON_DARK):
        self.add(
            f'<div style="position:absolute;left:{x}px;top:{y}px;width:{size}px;height:{size}px;display:flex;'
            f'flex-direction:column;background:{bg};border-radius:999px;justify-content:center;align-items:center;">'
            f'<svg preserveaspectratio="xMidYMid meet" style="width:{int(size * 0.55)}px;height:{int(size * 0.55)}px;'
            f'display:block" viewbox="0 0 100 100"><text dominant-baseline="central" fill="{fg}" '
            f'font-family="mc-anthropicons" font-size="90" text-anchor="middle" text-rendering="geometricPrecision" '
            f'x="50" y="54">{ICON[icon]}</text></svg></div>')

    # ---- зборка ----
    def render(self, total):
        bg = DARK_BG if self.dark else LIGHT_BG
        color = PAPER if self.dark else INK
        notes = f' data-speaker-notes="{esc(self.notes)}"' if self.notes else ""
        return (
            f'<section class="deck-slide" id="{self.index + 1}" aria-roledescription="slide" '
            f'aria-label="Slide {self.index + 1} of {total}" data-document-role="page" '
            f'data-label="{esc(self.label)}"{notes}><div class="deck-fit"><div class="deck-scaler">'
            f'<div class="slide" data-canvas-width="1920" data-canvas-height="1080" style="width:1920px;'
            f'height:1080px;position:relative;overflow:clip;contain:paint;box-sizing:border-box;background:{bg};'
            f'color:{color};font-family:\'Inter\', Arial, sans-serif;padding:128px;display:flex;flex-direction:column">'
            + "".join(self.parts) + "</div></div></div></section>")

    def motion(self):
        ids = [f for f, _ in self.frames]
        steps = [{"hidden": ids[:], "events": [], "auto": False}]
        for k, (fid, eff) in enumerate(self.frames):
            steps.append({"hidden": ids[k + 1:], "events": [{"id": fid, "effect": eff, "dir": "in"}],
                          "auto": False})
        return {"transition": "fade", "bg": (DARK_BG if self.dark else LIGHT_BG).lower(),
                "steps": steps, "embeds": []}


class Deck:
    def __init__(self, title, kind="python", topic=""):
        self.name = title
        self.kind = kind
        self.topic = topic
        self.header_text = "Урок Python" if kind == "python" else "Урок інформатики"
        self.header_icon = "code" if kind == "python" else "book"
        self.slides = []

    def slide(self, label, notes="", dark=False, blobs=None, header=True):
        s = Slide(self, len(self.slides), label, notes, dark, blobs, header)
        self.slides.append(s)
        return s

    def title(self, big, line1, line2, notes="", big_size=280, big_top=590, text_left=1180, text_top=760):
        """Титульний слайд: велике слово ліворуч унизу, підпис праворуч; декор додає викликач."""
        s = self.slide(big, notes, header=False,
                       blobs=[(980, 140, 940, 880, "50% 50%", 68), ("rot", 60, 40, 640, 360, -14)])
        s.header("Урок інформатики")
        s.topic_corner(self.topic)
        s.text(120, big_top, 1500, 290, esc(big), size=big_size, weight=700, lh=1, extra=";letter-spacing:-6px")
        s.text(text_left, text_top, 640, 60, line1, size=48, weight=600, lh=1.15)
        s.text(text_left, text_top + 70, 640, 40, line2, size=26, color=INK2, lh=1.35)
        return s

    # ---- типові слайди ----
    def plan(self, items, notes=""):
        s = self.slide("План уроку", notes, blobs=2)
        s.raw(f'<div style="position:absolute;left:1180px;top:0px;width:2px;height:1080px;background:{INK};'
              f'border-radius:0px;box-sizing:border-box"></div>')
        s.text(128, 640, 900, 280, "План<br/>уроку", size=128, weight=700, lh=1.02,
               extra=";letter-spacing:-3px")
        step = 66 if len(items) <= 10 else 58
        y = 150
        for i, it in enumerate(items, 1):
            s.text(1260, y, 60, 40, f"{i:02d}", size=26, weight=700, lh=1.4)
            s.text(1352, y + 2, 500, 40, it, size=28)
            y += step
        return s

    def your_turn(self, items, notes=""):
        """items: [(icon, text)]"""
        s = self.slide("Ваш хід!", notes, blobs=4)
        s.topic_corner(self.topic)
        s.text(120, 520, 620, 400, "Ваш<br/>хід!", size=190, weight=700, lh=0.98, extra=";letter-spacing:-6px")
        s.text(600, 590, 300, 90, "Завдання<br/>для практики", size=34, weight=600, lh=1.2)
        n = len(items)
        y = 540 - (n * 102) // 2
        for icon, t in items:
            s.icon_circle(960, y, icon)
            s.text(1056, y, 740, 68, t, size=31, valign="center")
            y += 102
        return s

    def task(self, label, notes="", where="За комп’ютером", title_size=58):
        s = self.slide(label, notes, blobs=0)
        s.h2(label, size=title_size, top=104)
        s.pill(where)
        return s

    def save(self, path):
        src = open(ENGINE_SOURCE, encoding="utf-8").read()
        a = src.find("<main")
        b = src.find("</main>")
        head, tail = src[:a], src[b:]
        head = re.sub(r"<title>.*?</title>", f"<title>{esc(self.name)}</title>", head, count=1)
        total = len(self.slides)
        motion = {"w": 1920, "h": 1080, "buildMs": 380,
                  "exitEasing": "cubic-bezier(0.45, 0, 0.85, 0.6)",
                  "effects": {"fade": {"transform": "", "easing": "cubic-bezier(0.2, 0.7, 0.2, 1)"},
                              "rise": {"transform": "translateY(48px)", "easing": "cubic-bezier(0.2, 0.7, 0.2, 1)"},
                              "scale": {"transform": "scale(0.8)", "easing": "cubic-bezier(0.2, 0.7, 0.2, 1)"},
                              "pop": {"transform": "scale(0.5)", "easing": "cubic-bezier(0.34, 1.56, 0.64, 1)"}},
                  "transMs": {"fade": 320, "push": 420, "magic": 480},
                  "transEase": "cubic-bezier(0.33, 0.01, 0.2, 1)", "live": True,
                  "slides": [s.motion() for s in self.slides]}
        mj = json.dumps(motion, ensure_ascii=False, separators=(",", ":"))
        head, n = re.subn(r'(<script type="application/json" id="deck-motion">).*?(</script>)',
                          lambda m: m.group(1) + mj + m.group(2), head, count=1, flags=re.S)
        assert n == 1, "не знайшов deck-motion у рушії"
        body = ('<main data-appifact-content style="font:16px / 24px ui-sans-serif, system-ui, sans-serif;'
                'color:rgb(11, 11, 11)">\n' + "\n".join(s.render(total) for s in self.slides) + "\n")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(head + body + tail)
        return path


def fit(code, width, size):
    """Зменшує шрифт моноширинного блоку, якщо найдовший рядок не влазить у ширину."""
    longest = max((len(l) for l in code.split("\n")), default=1)
    return min(size, int(width / (0.61 * max(1, longest))))


def run(code):
    """Виконує приклад і повертає те, що він надрукував, — щоб «ЕКРАН» на слайді завжди був правдивий."""
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(code, {})
    return buf.getvalue().rstrip("\n")


# ---------- справжні скриншоти tkinter / turtle ----------
import tempfile
SHOT_CACHE = os.environ.get("SLIDES_CACHE", os.path.join(tempfile.gettempdir(), "slides-cache"))


def shot(code, scenario=None, frames=None):
    """Запускає код на справжньому tkinter під Xvfb і повертає шлях до PNG.
    scenario — дії після старту (див. tkshot.py). Кешується за вмістом."""
    import hashlib
    import subprocess
    os.makedirs(SHOT_CACHE, exist_ok=True)
    sc = json.dumps(scenario or [], ensure_ascii=False)
    envkey = os.environ.get("TURTLE_SIZE", "") + os.environ.get("TURTLE_PEN", "")
    key = hashlib.md5((code + "\0" + sc + envkey + open(os.path.join(HERE, "tkshot.py")).read()).encode()).hexdigest()[:16]
    png = os.path.join(SHOT_CACHE, key + ".png")
    if not os.path.exists(png):
        src = os.path.join(SHOT_CACHE, key + ".py")
        scf = os.path.join(SHOT_CACHE, key + ".json")
        open(src, "w", encoding="utf-8").write(code)
        open(scf, "w", encoding="utf-8").write(sc)
        env = dict(os.environ)
        if "turtle" in code and "turtle.setup(" not in code:
            env.setdefault("TURTLE_SIZE", "[640, 480]")
        r = subprocess.run(["xvfb-run", "-a", "-s", "-screen 0 1280x1024x24", "/usr/bin/python3.12",
                            os.path.join(HERE, "tkshot.py"), src, png, scf],
                           capture_output=True, text=True, timeout=120, env=env)
        if r.returncode != 0 or not os.path.exists(png):
            raise RuntimeError("Приклад не запустився:\n" + code + "\n" + r.stderr[-2000:])
        open(png + ".out", "w").write(r.stdout)
    return png


def shot_info(png):
    """(ширина, висота, заголовок вікна, надруковане в консоль, повідомлення messagebox)"""
    from PIL import Image
    w, h = Image.open(png).size
    rd = lambda ext: open(png + ext, encoding="utf-8").read() if os.path.exists(png + ext) else ""
    return w, h, rd(".title"), rd(".out").rstrip("\n"), rd(".msg")


def data_uri(png):
    import base64
    return "data:image/png;base64," + base64.b64encode(open(png, "rb").read()).decode()


def onion(pngs, out_name):
    """Накладає кадри анімації один на одного: ранні — блідіші. Повертає шлях до PNG."""
    from PIL import Image, ImageChops
    ims = [Image.open(p).convert("RGB") for p in pngs]
    base = ims[-1].copy()
    white = Image.new("RGB", base.size, "white")
    acc = white.copy()
    n = len(ims)
    for k, im in enumerate(ims):
        alpha = 0.25 + 0.75 * (k / max(1, n - 1)) ** 2
        faded = Image.blend(white, im, alpha)
        acc = ImageChops.darker(acc, faded)
    path = os.path.join(SHOT_CACHE, out_name + ".png")
    acc.save(path)
    return path


def _window(self, x, y, w, png, title=None, dark=False):
    """Скриншот у рамці вікна з заголовком. Повертає (x0, y0, масштаб) — куди лягла точка (0,0) зображення."""
    iw, ih, t, _, _ = shot_info(png)
    title = t if title is None else title
    scale = w / iw
    h = int(ih * scale)
    bar = 46
    self.add(
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w + 4}px;height:{h + bar + 4}px;'
        f'background:#E6EAF0;border:2px solid {DARK_BG};border-radius:14px;box-sizing:border-box;overflow:hidden;'
        f'box-shadow:0 14px 40px rgba(30,40,60,0.22)">'
        f'<div style="position:absolute;left:0px;top:0px;width:100%;height:{bar}px;display:flex;flex-direction:row;'
        f'align-items:center;gap:10px;padding:0px 18px;box-sizing:border-box;border-bottom:2px solid {DARK_BG}">'
        f'<div style="width:14px;height:14px;border-radius:50%;background:#E8857A"></div>'
        f'<div style="width:14px;height:14px;border-radius:50%;background:#EFC56E"></div>'
        f'<div style="width:14px;height:14px;border-radius:50%;background:#8FC78A"></div>'
        f'<p style="margin-left:12px;font-size:22px;font-weight:600;color:{INK};white-space:nowrap;overflow:hidden">{esc(title)}</p></div>'
        f'<img alt="" src="{data_uri(png)}" style="position:absolute;left:0px;top:{bar}px;width:{w}px;height:{h}px;display:block"></div>')
    return x + 2, y + 2 + bar, scale


def _film(self, x, y, w, pngs, labels=None, gap=20):
    """Кадри анімації в ряд, як плівка."""
    n = len(pngs)
    fw = (w - gap * (n - 1)) / n
    for k, p in enumerate(pngs):
        iw, ih, *_ = shot_info(p)
        fh = ih * fw / iw
        fx = x + k * (fw + gap)
        self.add(f'<img alt="" src="{data_uri(p)}" style="position:absolute;left:{fx}px;top:{y}px;width:{fw}px;'
                 f'height:{fh}px;border:2px solid {DARK_BG};border-radius:8px;box-sizing:border-box">')
        if labels:
            self.text(int(fx), int(y + fh + 10), int(fw), 40, labels[k], size=24, weight=600, align="center",
                      color=self.ink2)
    return y + fh


def _marker(self, x, y, label, color=ORANGE, side="right"):
    """Точка з підписом координат поверх скриншота."""
    self.add(f'<div style="position:absolute;left:{x - 9}px;top:{y - 9}px;width:18px;height:18px;border-radius:50%;'
             f'background:{color};border:3px solid #fff;box-sizing:border-box;box-shadow:0 0 0 2px {color}"></div>')
    lx = x + 16 if side == "right" else x - 236
    al = "left" if side == "right" else "right"
    self.text(int(lx), int(y - 20), 220, 40, label, size=24, weight=700, mono=True, color=color, align=al)


Slide.window = _window
Slide.film = _film
Slide.marker = _marker
