# -*- coding: utf-8 -*-
"""
pidruchnyk2md.py — конвертер PDF-підручників «Генези» (серія Ривкінд Й.Я. та ін.) у Markdown.

Написаний і відлагоджений на «Інформатика. 9 клас» (Генеза, 2025, 296 с.).
Детальний опис підходу, налаштування під інший підручник і відомі обмеження — у README.md
поруч із цим файлом.

ЗАПУСК
    python3 pidruchnyk2md.py <вхід.pdf> [--out файл.md] [--title "Інформатика. 9 клас"]
                             [--source "Книги/pdf/9-клас.pdf"]
    Потрібен лише pymupdf (>=1.24). Без --out результат іде у stdout.

ЯК ЦЕ ПРАЦЮЄ (стисло)
    Текстового шару в цих PDF достатньо, OCR не потрібен. Ролі елементів (заголовок, рубрика,
    підпис до малюнка, тіло тексту) визначаються НЕ за евристикою «великий шрифт = заголовок»,
    а за конкретними іменами шрифтів верстки — див. role_of() і словники вгорі файлу.
    Це найкрихкіша частина: у підручнику іншого року/класу імена шрифтів можуть відрізнятися,
    тому перед конвертацією нової книжки завжди роби інвентаризацію шрифтів (див. README).

    Підручник має ДВА режими верстки, які обробляються по-різному (див. regime):
      • "school" — основна верстка InDesign: тіло SchoolBook_Alx 11, заголовки AvantGarde~Alx-Bold.
                   Абзац починається з відступу першого рядка (~+20 pt) — flow="indent".
      • "times"  — вставлені розділи, зверстані у Word (Times New Roman 14; у 9 класі це
                   розділ 5 і Словник). Там кожен рядок = окремий PDF-блок, відступів немає,
                   тому межа абзацу визначається «неповнотою» рядка — flow="full".
      Режим обирається за шириною сторінки (Word-сторінки ширші: 595 pt проти 459 pt).

КОНВЕЄР
    process_page()  -> відсіює службові блоки (колонцифри, колонтитули, підписи всередині схем),
                       знаходить таблиці, визначає бічні врізки, класифікує блоки за ролями
    emit()          -> перетворює впорядкований список блоків у Markdown
    render_stream() -> найскладніше: збирає рядки в абзаци / списки / блоки коду
    runs_md()       -> інлайнове форматування (жирний, курсив) на рівні спанів
"""
import argparse
import contextlib
import re, sys
import pymupdf

# ---------------------------------------------------------------------------
# Маркери списків. Ключ — символ, значення — рівень вкладеності.
# У «шкільній» верстці ієрархія ● > ○ > ■ ; ► вживається на шмуцтитулах розділів.
# Порожні на вигляд ключі — символи Symbol/Wingdings з приватної зони Unicode (U+F0xx),
# саме так Word кодує свої маркери; \x07 — «невидимий» маркер Symbol.
# ---------------------------------------------------------------------------
BULLET_LEVEL = {
    "\u25cf": 0,   # ●  верхній рівень
    "\u25cb": 1,   # ○  другий рівень
    "\u25a0": 2,   # ■  третій рівень
    "\u25ba": 0,   # ►  переліки на шмуцтитулах розділів
    "\u2022": 0,   # •  Symbol, розділ 5
    "\x07": 1,     #    «невидимий» маркер Symbol
    "o": 1,         # o  Courier New як маркер другого рівня у Word
    "\uf0d8": 0,   # ➢  Wingdings
    "\uf0b7": 0,   # •  Symbol (приватна зона)
    "\uf0a7": 1,   # ▪  Wingdings
    "\uf0fc": 0,   # ✔  Wingdings
    "\uf02d": 0,   # –  Symbol
    "\u203a": 0,   # ›  переліки на шмуцтитулах 5 класу
    ">": 0,        # >  те саме, набране звичайною «більше»
    # Дефіс і тире НЕ вносимо сюди: у тексті вони трапляються надто часто.
    # Їх розпізнає leading_bullet() окремо — лише коли після знака є помітний відступ.
}
BULLET_CHARS = "".join(BULLET_LEVEL)
# Шрифти, якими набрано САМІ значки маркерів (їхній текст ніколи не є змістом).
BULLET_FONTS = ("Garamond", "BloggerSans", "SymbolMT", "Wingdings", "CourierNewPSMT", "Webdings")
# Суто декоративні написи на берегах: назва розділу вертикально + велика цифра розділу.
DECOR_FONTS = ("Rodeo~Alx-Bold", "CourierNewPS-BoldMT")
# Написи на берегах сторінки («РОЗДІЛ» вертикально + цифра розділу). На відміну від
# решти DECOR_FONTS, сюди НЕ входить Rodeo~Alx-Bold — ним набрано назви розділів.
MARGIN_FONTS = ("CourierNewPS-BoldMT",)
# --- верстка "digital" (5 клас) ---
DG_CHAPTER = ("MyriadPro-Black",)            # назва розділу, 46 pt
DG_HEAD = ("MyriadPro-BlackSemiExt",)        # «Тема N» + назва теми, підзаголовки
DG_RUBRIC = ("MyriadPro-Black", "MyriadPro-Bold", "SegoeUI-Bold", "OpenSans-Semibold",
             "Calibri-Bold", "SegoeUIBlack")
DG_ITALIC = ("SegoeUI-Italic", "SegoeUI-SemiboldItalic", "OpenSans-Italic")
# ---------------------------------------------------------------------------
# ПРОФІЛІ КНИЖОК. Верстка серії однакова, але кеглі різняться від класу до класу,
# тому ролі заголовків задаються тут, а не «на око» в role_of().
#   ag_intro / ag_sub / ag_point — пороги кеглів AvantGarde~Alx-Bold:
#       >= ag_intro          → звертання у вступі (intro)
#       >= ag_point + «N.M.» → заголовок пункту (point)
#       >= ag_sub            → підзаголовок пункту (sub)
#       нижче                → назва рубрики (rubric)
#   allow_times  — чи є в книжці розділи, зверстані у Word (широкі сторінки).
#                  У 7 і 8 класах широких сторінок немає (у 7 класі широкі сторінки —
#                  це розвороти-ілюстрації), тож режим "times" вимкнено.
#   fix_cp1251   — чи лагодити кодування тексту (див. demojibake()).
# ---------------------------------------------------------------------------
PROFILES = {
    "9": dict(body=11.0, ag_intro=11.5, ag_sub=10.3, ag_point=10.3,
              allow_times=True,  fix_cp1251=False, dehyphenate=False),
    "8": dict(body=11.0, ag_intro=11.5, ag_sub=10.3, ag_point=10.3,
              allow_times=False, fix_cp1251=False, dehyphenate=True),
    "7": dict(body=12.0, ag_intro=12.5, ag_sub=10.4, ag_point=10.8,
              allow_times=False, fix_cp1251=True,  dehyphenate=True),
    # 5 клас — зовсім інша книжка (Дж. Е. Біос «Цифрові підлітки», Binary Logic/
    # «Лінгвіст»): A4, журнальна верстка, шрифти Segoe UI + Myriad Pro, переносів
    # немає, зате багато виносок-пояснень навколо скриншотів. Див. layout="digital".
    "5": dict(body=11.5, layout="digital", page_offset=1, indent_min=6, code=False,
              allow_times=False, fix_cp1251=False, dehyphenate=False),
}
_DEFAULTS = dict(layout="school", page_offset=0, indent_min=12, code=True,
                 ag_intro=11.5, ag_sub=10.3, ag_point=10.3)
for _p in PROFILES.values():
    for _k, _v in _DEFAULTS.items():
        _p.setdefault(_k, _v)
PROF = PROFILES["9"]

# ---------------------------------------------------------------------------
# Лагодження кодування (потрібне для 7 класу).
# У тому PDF шрифти SchoolBook_Alx / AvantGarde мають зіпсовану таблицю ToUnicode:
# байти cp1251 віддаються як символи Latin-1, тому «Учні» читається як «Ó÷íі».
# Це оборотно без втрат: досить прочитати символ назад як байт cp1251.
# Перетворюємо ЛИШЕ ті символи, для яких cp1251 дає кирилицю, тому ASCII (Python,
# HTTP), лапки «», © і вже правильні і/ї/є/ґ лишаються недоторканими.
# ---------------------------------------------------------------------------
def _cp1251_map():
    m = {}
    for code in range(0x80, 0x100):
        try:
            u = bytes([code]).decode("cp1251")
        except UnicodeDecodeError:
            continue
        if "\u0400" <= u <= "\u04ff":
            m[chr(code)] = u
    return str.maketrans(m)

CP1251_TR = _cp1251_map()

CP1251_BROKEN = set(CP1251_TR)          # коди символів, які варто перекодувати

def _looks_mojibake(t):
    """Чи цей фрагмент — зіпсована кирилиця (для книжок, де це поодинокі рядки).

    У 8 і 9 класах текстовий шар цілий, але подекуди лишився рядок у cp1251
    (напр. копірайт на звороті титулу). Ознака: кілька символів, які читаються
    як кирилиця, і жодної справжньої кирилиці поруч. Перевірка навмисне сувора,
    щоб не зачепити «24 × 5» (× теж із Latin-1).
    """
    mappable = sum(1 for c in t if ord(c) in CP1251_BROKEN)
    if mappable < 3:
        return False
    if any("\u0400" <= c <= "\u04ff" for c in t):
        return False
    other = sum(1 for c in t if ord(c) > 0x7F and ord(c) not in CP1251_BROKEN and not c.isspace())
    return mappable >= 2 * max(1, other)

def demojibake(t):
    if PROF["fix_cp1251"]:
        return t.translate(CP1251_TR)
    return t.translate(CP1251_TR) if _looks_mojibake(t) else t

def page_dict(page):
    """page.get_text("dict") з полагодженим кодуванням спанів."""
    d = page.get_text("dict")
    for b in d["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            for sp in l["spans"]:
                sp["text"] = demojibake(sp["text"])
    return d

NUM_HEAD = re.compile(r"^\d+\.\s?\d+\.")
CHAPTER_HEAD = re.compile(r"^Розділ\s+\d+\.")
CYR = re.compile(r"[а-щьюяєіїґА-ЩЬЮЯЄІЇҐ]")

def clean(t):
    return re.sub(r"[ \t]+", " ", t.replace("\xa0", " ").replace("\xad", ""))

# ------------------------------------------------------------------ рядки
def is_bullet_font(f):
    return f.startswith(BULLET_FONTS)

def line_runs(spans, keep_bullets=False):
    """Список [текст, жирний, курсив]; маркери списку відкидаються (або нормалізуються)."""
    runs = []
    for s in spans:
        t = s["text"]
        if not t or s["font"].startswith(DECOR_FONTS):
            continue
        if is_bullet_font(s["font"]):
            if keep_bullets:
                t = "".join("●" if c in BULLET_CHARS else c for c in t)
            else:
                t = "".join(c for c in t if c not in BULLET_CHARS)
            if not t.strip():
                continue
        b = "Bold" in s["font"]
        i = "Italic" in s["font"] or "Itali" in s["font"]
        if runs and runs[-1][1] == b and runs[-1][2] == i:
            runs[-1][0] += t
        else:
            runs.append([t, b, i])
    return runs

OPEN = {")": "(", "»": "«", "]": "["}
CLOSE = {"(": ")", "«": "»", "[": "]"}

def runs_md(runs):
    runs = list(runs)
    for k in range(len(runs) - 1):
        a, c = runs[k], runs[k + 1]
        for x, y in ((a, c), (c, a)):
            if len(x[0].strip()) <= 3 and x[0].strip() and not x[0].startswith(" ") \
                    and (x[1], x[2]) != (y[1], y[2]) and (y[1] or y[2]) \
                    and (x[1] >= y[1] and x[2] >= y[2]):
                x[1], x[2] = y[1], y[2]
                break
    merged = []
    for t, b, i in runs:
        if merged and not CYR.search(t) and not re.search(r"[0-9A-Za-z]", t):
            merged[-1][0] += t          # самі розділові знаки — без зміни стилю
            continue
        if merged and merged[-1][1] == b and merged[-1][2] == i:
            merged[-1][0] += t
        else:
            merged.append([t, b, i])
    out = []
    for t, b, i in merged:
        t = clean(t)
        if not t:
            continue
        if not (b or i) or not t.strip():
            out.append(t); continue
        lead = t[: len(t) - len(t.lstrip())]
        trail = t[len(t.rstrip()):]
        core = t.strip()
        m = re.search(r"[.,;!?]+$", core)
        if m and len(m.group(0)) < len(core):
            trail = m.group(0) + trail
            core = core[: -len(m.group(0))]
        while len(core) > 1 and core[-1] in ")»]" and core.count(OPEN[core[-1]]) < core.count(core[-1]):
            trail = core[-1] + trail
            core = core[:-1]
        while len(core) > 1 and core[-1] in "(«[":
            trail = core[-1] + trail
            core = core[:-1]
        while len(core) > 1 and core[0] in "«([" and core.count(CLOSE[core[0]]) < core.count(core[0]):
            lead += core[0]
            core = core[1:]
        while len(core) > 1 and core[0] in ")»]":
            lead += core[0]
            core = core[1:]
        mark = "***" if (b and i) else ("**" if b else "*")
        out.append(f"{lead}{mark}{core}{mark}{trail}")
    s = "".join(out)
    s = re.sub(r"\*\*\*(\s+)\*\*\*", r"\1", s)
    s = re.sub(r"\*\*(\s+)\*\*", r"\1", s)
    s = re.sub(r"(?<!\*)\*(\s+)\*(?!\*)", r"\1", s)
    return re.sub(r"  +", " ", s)

def runs_text(runs):
    return clean("".join(r[0] for r in runs))

def _line_size(l):
    sp = [x for x in l["spans"] if x["text"].strip()]
    return max((x["size"] for x in sp), default=0.0)

def merge_split_blocks(blocks):
    """Склеює PDF-блоки, між якими розірвано ОДИН рядок тексту.

    У цих книжках сторінку часто складено з плиток-зображень, і рядок, що перетинає
    межу плитки, потрапляє у два-три різні блоки, ще й у довільному порядку:
        [блок 75] «ьому розділі ви отримаєте нові…»   [блок 79] «У ць»   [блок 77] «ите»
    Без склеювання кожен уламок стає окремим абзацом. Ознака розриву — спільна базова
    лінія, невелика горизонтальна щілина і однаковий кегль.
    Кожен рядок отримує поле "_src" (номер вихідного блока), щоб visual_lines()
    знала, які фрагменти прийшли ззовні, і не зшивала через усю сторінку.
    """
    # Той самий рядок часто намальовано в PDF по кілька разів (по разу на кожну
    # плитку-зображення, що його перекриває) — інакше заголовок потрапляє в текст
    # двічі-чотири рази поспіль. Дублем вважаємо збіг тексту І позиції.
    seen = set()
    items = []
    for i, b in enumerate(blocks):
        if b["type"] != 0:
            continue
        lines = []
        for l in b["lines"]:
            txt = "".join(sp["text"] for sp in l["spans"]).strip()
            if not txt:
                continue
            # Декоративні написи на берегах («РОЗДІЛ» вертикально, цифра розділу)
            # відкидаємо ДО склеювання: інакше вони чіпляються до кінця рядка тексту
            # і ховають дефіс переносу.
            if all(sp["font"].startswith(MARGIN_FONTS)
                   for sp in l["spans"] if sp["text"].strip()):
                continue
            # Повернутий рядок — вертикальний колонтитул на березі (5 клас).
            # Лише для журнальної верстки: у книжках «Генези» повернутим буває
            # і текст усередині схем, який досі потрапляв у вивід.
            if PROF["layout"] == "digital" \
                    and tuple(round(x, 2) for x in l.get("dir", (1, 0))) != (1.0, 0.0):
                continue
            key = (txt, round(l["bbox"][0]), round(l["bbox"][1]))
            if key in seen:
                continue
            seen.add(key)
            lines.append(l)
        if not lines:
            continue
        for l in lines:
            l["_src"] = i
        items.append({"idx": i, "block": b, "lines": lines})

    def adjacent(a, c):
        # Склеюємо лише тоді, коли хоча б один бік — короткий уламок. Інакше під
        # це правило потрапляють дві колонки Словника, і рядки колонок зшиваються
        # навхрест («множина сим-» + «силання комп'ютерними мережами»).
        if len(a["lines"]) > 2 and len(c["lines"]) > 2:
            return False
        for la in a["lines"]:
            for lc in c["lines"]:
                if abs(la["bbox"][1] - lc["bbox"][1]) >= 3:
                    continue
                if abs(_line_size(la) - _line_size(lc)) > 0.75:
                    continue
                # беремо ту зі щілин, що відповідає реальному сусідству
                # (друга при цьому — від'ємна на всю ширину рядка)
                gap = max(lc["bbox"][0] - la["bbox"][2], la["bbox"][0] - lc["bbox"][2])
                if -8 <= gap < 14:
                    return True
        return False

    changed = True
    while changed:
        changed = False
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                if adjacent(items[i], items[j]):
                    items[i]["lines"] += items[j]["lines"]
                    del items[j]
                    changed = True
                    break
            if changed:
                break

    out = []
    for it in items:
        xs = [l["bbox"] for l in it["lines"]]
        bbox = (min(b[0] for b in xs), min(b[1] for b in xs),
                max(b[2] for b in xs), max(b[3] for b in xs))
        out.append(dict(it["block"], lines=it["lines"], bbox=bbox, number=it["idx"]))
    out.sort(key=lambda b: (round(b["bbox"][1] / 4), b["bbox"][0]))
    return out

def _drop_prefix(spans, k):
    """Викидає k перших символів із послідовності спанів."""
    out, left = [], k
    for sp in spans:
        if left <= 0:
            out.append(sp)
            continue
        t = sp["text"]
        if len(t) <= left:
            left -= len(t)
            continue
        out.append(dict(sp, text=t[left:]))
        left = 0
    return out

def visual_lines(block):
    """Об'єднує фрагменти, що лежать на одній базовій лінії."""
    raw = []
    for l in block["lines"]:
        if not "".join(s["text"] for s in l["spans"]).strip():
            continue
        raw.append(l)
    raw.sort(key=lambda l: (round(l["bbox"][1] / 3.0), l["bbox"][0]))
    out = []
    for l in raw:
        frag = clean("".join(s["text"] for s in l["spans"])).strip()
        if out and abs(l["bbox"][1] - out[-1]["y"]) < 4 and l["bbox"][0] < out[-1]["x1"] - 2 \
                and frag and all(c in BULLET_CHARS + " " for c in frag):
            continue                      # дубль маркера списку поверх тексту
        gap = l["bbox"][0] - out[-1]["x1"] if out else 0
        foreign = bool(out) and l.get("_src") != out[-1].get("_src")
        joinable = gap >= (-8 if foreign else -2) and (gap < 20 or not foreign)
        if out and abs(l["bbox"][1] - out[-1]["y"]) < 4 and joinable:
            cur = out[-1]
            if foreign and gap < 0:
                # Фрагменти перекриваються: літеру на межі плитки намальовано двічі
                # («У ць» + «ьому» -> «У цььому»). Знімаємо повтор.
                atail = "".join(sp["text"] for sp in cur["spans"])
                bhead = "".join(sp["text"] for sp in l["spans"])
                for k in range(min(4, len(atail), len(bhead)), 0, -1):
                    if atail[-k:] == bhead[:k]:
                        l = dict(l, spans=_drop_prefix(l["spans"], k))
                        break
            if gap > 2 and cur["spans"] and not cur["spans"][-1]["text"].endswith(" "):
                cur["spans"] = cur["spans"] + [dict(l["spans"][0], text=" ")]
            cur["spans"] = cur["spans"] + list(l["spans"])
            cur["x1"] = l["bbox"][2]
        else:
            out.append(dict(spans=list(l["spans"]), y=l["bbox"][1],
                            x0=l["bbox"][0], x1=l["bbox"][2], _src=l.get("_src")))
    for l in out:
        l["raw"] = "".join(s["text"] for s in l["spans"])
        l["txt"] = clean(l["raw"])
        l["fonts"] = {(s["font"], round(s["size"], 1)) for s in l["spans"] if s["text"].strip()}
        stats = {}
        for sp in l["spans"]:
            t = sp["text"].strip()
            if not t:
                continue
            k = (sp["font"], round(sp["size"], 1))
            stats[k] = stats.get(k, 0) + len(t)
        l["fontw"] = stats
    return out

def dominant(ln):
    """Головний шрифт рядка — той, яким набрано найбільше символів.

    ВАЖЛИВО: раніше тут брався довільний елемент множини шрифтів, через що результат
    конвертації залежав від хешування рядків і мінявся від запуску до запуску.
    Тепер порядок детермінований: (кількість символів, кегль, порядок появи).
    """
    stats = ln.get("fontw") or {}
    pool = [(f, n, i) for i, (f, n) in enumerate(stats.items()) if not is_bullet_font(f[0])]
    if not pool:
        pool = [(f, n, i) for i, (f, n) in enumerate(stats.items())]
    if not pool:
        return ("", 0)
    f, _n, _i = max(pool, key=lambda t: (t[1], t[0][1], -t[2]))
    return f

def glyph_only(ln):
    t = ln["txt"].strip()
    return bool(t) and all(c in BULLET_CHARS + " " for c in t)

def leading_bullet(ln):
    t = ln["txt"].lstrip()
    if not t:
        return None
    c = t[0]
    if c == ">" and (PROF["layout"] != "digital" or len(t) < 2 or t[1] != " "):
        return None
    if c in BULLET_LEVEL and c not in "o":
        return BULLET_LEVEL[c]
    if c == "o" and len(t) > 1 and t[1] == " ":
        if any(f[0].startswith("CourierNew") for f in ln["fonts"]):
            return 1
        return None
    if c in "-–" and len(t) > 1 and t[1] == " ":
        # тире як маркер списку: після нього — помітний відступ до тексту
        sp = [s for s in ln["spans"] if s["text"].strip()]
        if len(sp) >= 2 and sp[0]["text"].strip() in "-–" \
                and sp[1]["bbox"][0] - sp[0]["bbox"][2] > 15:
            return 0
    return None

def strip_leading_bullet(runs):
    out = [list(r) for r in runs]
    while out:
        t = out[0][0]
        s = t.lstrip()
        if not s:
            out.pop(0); continue
        if s[0] in BULLET_CHARS:
            out[0][0] = s[1:]
            continue
        break
    if out:
        out[0][0] = re.sub(r"^[\s\-–]+", "", out[0][0])
    return out

# ------------------------------------------------------------------ код
CODE_RE = re.compile(r"[=()\[\]]|:\s*$")
KEYWORD_RE = re.compile(r"^\s*(if|else|elif|for|while|def|return|print|import|from|input|not|and|or)\b")

def is_code(ln, body_left, bodywidth):
    """Чи є рядок фрагментом коду Python.

    Для книжок без лістингів (5 клас) вимикається профілем: code=False.

    У цій верстці код набрано ТИМ САМИМ жирним накресленням, що й виділення в тексті
    (SchoolBook_Alx-Bold), тому одного шрифту замало. Додаткові умови: рядок зсунуто вправо
    від лівого поля сторінки, він короткий, у ньому мало кирилиці (лапки та коментар після #
    з підрахунку виключаємо) і є ознаки коду — дужки, «=» або ключове слово Python.
    """
    if not PROF["code"]:
        return False
    txt = ln["txt"].strip()
    if not txt:
        return False
    real = [f for f in ln["fonts"] if not is_bullet_font(f[0])]
    if not real:
        return False
    has_comment = "#" in txt
    allowed = {"SchoolBook_Alx-Bold", "CourierNewPS-BoldMT"}
    if has_comment:
        allowed |= {"SchoolBook_Alx", "SchoolBook_Alx-Italic"}
    if not all(f[0] in allowed for f in real):
        return False
    first = next((sp for sp in ln["spans"] if sp["text"].strip()), None)
    if first is None or "Bold" not in first["font"]:
        return False
    if ln["x0"] < body_left + 14:
        return False
    maxw = 0.98 if has_comment else 0.72
    if (ln["x1"] - ln["x0"]) > maxw * bodywidth or len(txt) > 110:
        return False
    probe = re.sub(r"[\u2018\u2019\u201c\u201d'\"].*?[\u2018\u2019\u201c\u201d'\"]", "", txt)
    probe = probe.split("#")[0]
    letters = [c for c in probe if c.isalpha()]
    cyr_ratio = (sum(1 for c in letters if CYR.match(c)) / len(letters)) if letters else 0
    if cyr_ratio > 0.4 and not KEYWORD_RE.match(txt):
        return False
    return bool(CODE_RE.search(probe) or KEYWORD_RE.match(txt))

# ------------------------------------------------------------------ потік тексту
ORD_RE = re.compile(r"^\s*(\d{1,2})\.\s*\t")

def render_stream(groups, body_left, bodywidth, flow="indent"):
    """groups — список (block_left, block_right, [visual lines]) -> блоки Markdown.

    Найскладніша функція. Збирає рядки в абзаци, списки та блоки коду.
    Ключові правила:
      • перенос слова (м'який дефіс U+00AD у кінці рядка) ЗАВЖДИ склеює рядки — має
        пріоритет над усіма правилами розриву;
      • flow="indent": новий абзац там, де рядок починається з відступу (x0 >= bleft+12);
      • flow="digital": рядки вирівняні по центру, відступів немає і права межа нічого не
        каже, тож абзац завершує лише розділовий знак у кінці рядка (5 клас);
      • flow="full": новий абзац там, де попередній рядок «неповний» (не дотягує до правого
        поля) і закінчується крапкою/двокрапкою — для верстки з Word;
      • продовження пункту МАРКОВАНОГО списку має висячий відступ управо (x0 >= list_left+8);
      • продовження пункту НУМЕРОВАНОГО списку в рубриках, навпаки, повертається до лівого
        поля, тому для нього правило інше — див. гілку bullets[-1][3] is not None.
    """
    out = []
    para = None
    bullets = []          # [level, runs, last_raw, number|None]
    list_left = None
    code = []             # [x0, text]
    pending_level = None

    def flush_para():
        nonlocal para
        if para and runs_text(para[0]).strip():
            out.append(("p", runs_md(para[0]).strip()))
        para = None

    def flush_code():
        nonlocal code
        if code:
            base = min(c[0] for c in code)
            body = []
            for x, t, _r in code:
                ind = max(0, int(round((x - base) / 19.0))) * 4
                body.append(" " * ind + t)
            out.append(("code", body))
        code = []

    def flush_bullets():
        nonlocal bullets, list_left
        items = []
        for lvl, runs, _, num in bullets:
            md = runs_md(runs).strip()
            parts = [p.strip() for p in re.split(r"\s*●\s*", md) if p.strip()]
            for p in (parts or [md]):
                items.append((lvl, p, num))
        if items:
            out.append(("ul", items))
        bullets, list_left = [], None

    ragged = flow in ("full", "digital")

    def full(ln, bright):
        if flow == "digital":
            return not re.search(r"[.!?:;»]\s*$", ln["txt"].strip())
        if ln["x1"] > bright - 14:
            return True
        if flow == "full" and not re.search(r"[.!?:;»]\s*$", ln["txt"].strip()):
            return True
        return False

    prev_full = None
    last_raw = ""
    for bleft, bright, lines in groups:
        for ln in lines:
            hyph = is_hyphen_break(last_raw)
            last_raw = ln["raw"]
            if glyph_only(ln):
                flush_para(); flush_code()
                pending_level = BULLET_LEVEL.get(ln["txt"].strip()[0], 0)
                if list_left is None or (not bullets) or pending_level <= bullets[-1][0]:
                    list_left = ln["x0"]
                continue
            if is_code(ln, body_left, bodywidth):
                flush_para(); flush_bullets()
                code.append([ln["x0"], ln["txt"].strip(), ln["raw"]])
                prev_full = False
                continue
            if code and ln["x0"] > body_left + 80 and "#" in code[-1][1] \
                    and not any("Bold" in f[0] for f in ln["fonts"]):
                sep = "" if is_hyphen_break(code[-1][2]) else " "
                code[-1][1] = code[-1][1].rstrip() + sep + ln["txt"].strip()
                code[-1][2] = ln["raw"]
                continue
            flush_code()
            runs = line_runs(ln["spans"], keep_bullets=True)
            om = ORD_RE.match(ln["raw"])
            lvl, num = pending_level, None
            lb = leading_bullet(ln)
            if om:
                flush_para()
                lvl, num = 0, int(om.group(1))
                runs = line_runs(ln["spans"])
                runs = strip_ord(runs)
                list_left = ln["x0"]
            elif lb is not None:
                lvl = lb
                runs = strip_leading_bullet(line_runs(ln["spans"]))
                list_left = ln["x0"]
            if lvl is not None and runs_text(runs).strip():
                if bullets and bullets[-1][3] is not None and num is None and lb is None and not om:
                    pass
                flush_para()
                bullets.append([lvl, runs, ln["raw"], num])
                pending_level = None
                prev_full = full(ln, bright)
                continue
            pending_level = None
            if ragged:
                cont = bullets and (prev_full is True or hyph)
            elif bullets and bullets[-1][3] is not None:
                # нумерований пункт: продовження може повертатися до лівого поля
                cont = hyph or not (ln is lines[0] and prev_full is False
                                    and ln["x0"] >= bleft + PROF["indent_min"])
            else:
                cont = bullets and list_left is not None and (ln["x0"] >= list_left + 8 or hyph) \
                    and not (ln is lines[0] and prev_full is False and not hyph)
            if cont:
                item = bullets[-1]
                item[1] = merge_runs(item[1], item[2], line_runs(ln["spans"]))
                item[2] = ln["raw"]
                prev_full = full(ln, bright)
                continue
            flush_bullets()
            runs = line_runs(ln["spans"])
            if ragged:
                newpara = not (prev_full is True or hyph)
            else:
                newpara = ln["x0"] >= bleft + PROF["indent_min"] and not hyph
                if para is not None and not newpara and prev_full is False and ln is lines[0] and not hyph:
                    newpara = True
            if para is None or newpara:
                flush_para()
                para = [runs, ln["raw"]]
            else:
                para[0] = merge_runs(para[0], para[1], runs)
                para[1] = ln["raw"]
            prev_full = full(ln, bright)
    flush_code(); flush_bullets(); flush_para()
    return out

def strip_ord(runs):
    out = [list(r) for r in runs]
    if out:
        out[0][0] = re.sub(r"^\s*\d{1,2}\.\s*", "", out[0][0])
    return out

# У 9 класі перенос слова позначено м'яким дефісом (U+00AD), і його досить викинути.
# У 7 і 8 класах у тексті стоїть ЗВИЧАЙНИЙ дефіс — тобто «відомос-» + «ті» треба зшити
# в «відомості», інакше в тексті лишається близько 2000 розірваних слів.
# Виняток — складні слова та абревіатури (QR-кодом, URL-адрес, USB-флешнакопичувач):
# там дефіс частина слова, його зберігаємо; якщо ж далі йде сполучник, це «висячий»
# дефіс («GIF- та WebP-анімації») і потрібен ще й пробіл.
# Останнє «слово» перед дефісом — суцільна абревіатура/число (QR, URL, USB, 3D)
# або шматок адреси: тоді дефіс належить слову, а не переносу.
CAPS_TAIL = re.compile(r"(?:^|[\s(«\"„/])[A-ZА-ЯЇІЄҐ0-9]{2,}$")
URLISH = re.compile(r"[^\s]*[./@][^\s]*$")
CONJ = {"та", "і", "й", "чи", "або"}

def is_hyphen_break(raw):
    """Чи рядок обірвано переносом — сигнал, що наступний рядок продовжує абзац."""
    p = raw.replace("\xa0", " ").rstrip()
    if p.endswith("\xad"):
        return True
    return bool(PROF["dehyphenate"] and len(p) > 1 and p.endswith("-") and p[-2].isalnum())

def _keeps_hyphen(core):
    return bool(CAPS_TAIL.search(core) or URLISH.search(core))

def join_mode(prev_raw, next_raw):
    """Як приєднати наступний рядок абзацу: soft / strip / tight / space."""
    p = prev_raw.replace("\xa0", " ").rstrip()
    n = next_raw.lstrip()
    if p.endswith("\xad"):
        return "soft"
    if p.endswith("-") and len(p) > 1 and n and (n[0].isalnum()):
        core = p[:-1]
        if core[-1:].isalnum():
            if not PROF["dehyphenate"]:
                # 9 клас: перенос позначено м'яким дефісом, тож звичайний дефіс
                # у кінці рядка — завжди частина слова («3D-модель», «будь-який»).
                return "tight"
            if not n[0].islower() or _keeps_hyphen(core):
                word = re.match(r"[^\s,;:.!?]+", n)
                if word and word.group(0).lower() in CONJ:
                    return "tight_space"      # висячий дефіс: «GIF- та WebP-»
                return "tight"
            return "strip"
    return "space"

def merge_runs(runs, prev_raw, new_runs):
    runs = [list(r) for r in runs]
    new_runs = [list(r) for r in new_runs]
    if not new_runs:
        return runs
    if not runs:
        return new_runs
    mode = join_mode(prev_raw, "".join(r[0] for r in new_runs))
    tail = runs[-1][0].rstrip()
    if mode == "soft":
        runs[-1][0] = tail[:-1] if tail.endswith("\xad") else tail
    elif mode == "strip":
        runs[-1][0] = tail[:-1] if tail.endswith("-") else tail
    elif mode == "tight":
        runs[-1][0] = tail
    elif mode == "tight_space":
        runs[-1][0] = tail + " "
    else:
        runs[-1][0] = tail + " "
    new_runs[0][0] = new_runs[0][0].lstrip()
    if runs[-1][1] == new_runs[0][1] and runs[-1][2] == new_runs[0][2]:
        runs[-1][0] += new_runs[0][0]
        new_runs = new_runs[1:]
    return runs + new_runs

# ------------------------------------------------------------------ таблиці
def unwrap_cell(text):
    """Склеює перенесені рядки всередині комірки таблиці за тими самими правилами,
    що й у звичайному тексті (комірки видобуваються окремо від основного потоку)."""
    parts = text.replace("\xad\n", "\xad").split("\n")
    acc = parts[0]
    for nxt in parts[1:]:
        mode = join_mode(acc, nxt)
        tail = acc.rstrip()
        if mode == "soft":
            acc = (tail[:-1] if tail.endswith("\xad") else tail) + nxt.lstrip()
        elif mode == "strip":
            acc = (tail[:-1] if tail.endswith("-") else tail) + nxt.lstrip()
        elif mode == "tight":
            acc = tail + nxt.lstrip()
        else:
            acc = tail + " " + nxt.lstrip()
    return acc.replace("\xad", "")

def good_table(t):
    try:
        data = t.extract()
    except Exception:
        return None
    if not data or len(data) < 2:
        return None
    ncol = max(len(r) for r in data)
    if ncol < 2:
        return None
    filled = sum(1 for r in data for c in r if (c or "").strip())
    if filled < 0.45 * len(data) * ncol:
        return None
    if sum(1 for c in data[0] if (c or "").strip()) < 2:
        return None
    rows = []
    for r in data:
        cells = [clean(unwrap_cell(demojibake(c or ""))).strip() for c in r]
        cells += [""] * (ncol - len(cells))
        rows.append([c.replace("|", "\\|") for c in cells])
    return rows

def table_md(rows):
    out = ["| " + " | ".join(rows[0]) + " |",
           "|" + "|".join([" --- "] * len(rows[0])) + "|"]
    for r in rows[1:]:
        out.append("| " + " | ".join(r) + " |")
    return out

# ------------------------------------------------------------------ ролі блоків
def _role_digital(lines, font, size, t0):
    """Ролі у верстці 5 класу. Заголовок визначає НАЙБІЛЬШИЙ шрифт блока: «Тема 1»
    (14 pt) і назва теми (19 pt) лежать в одному блоці, і за першим рядком роль вийшла б
    хибною. «Практичне завдання» набрано тим самим 19 pt, але внизу сторінки, — тож
    заголовки тем відрізняємо за розташуванням угорі."""
    big_f, big_sz = font, size
    for l in lines:
        for f, sz in l["fonts"]:
            if sz > big_sz:
                big_f, big_sz = f, sz
    y = lines[0]["y"]
    alltext = " ".join(l["txt"] for l in lines).strip()
    if big_f.startswith(DG_CHAPTER) and big_sz >= 30:
        return "chapter_title"
    if big_f.startswith(DG_HEAD):
        if big_sz >= 17:
            return "point" if y < 130 else "sub"
        if big_sz >= 12.5:
            return "sub"
    if big_sz >= 12.5 and big_f.startswith(DG_RUBRIC) and len(alltext) <= 120:
        return "rubric"
    return "body"

def role_of(lines, regime, pno):
    """Роль блока за шрифтом його першого рядка. ГОЛОВНА ТОЧКА НАЛАШТУВАННЯ під іншу книжку.

    Ролі: chapter_title / chapter_plain (##), point (###), sub, intro, letter (####),
          rubric (**жирний рядок**), caption / table_caption (*курсив*), body (звичайний текст).
    Розміри AvantGarde у «шкільній» верстці 9 класу:
        12.0 — звертання у вступі;  10.5 — підзаголовок пункту;  10.0 — назва рубрики;
         9.5 — або заголовок пункту «N.M. НАЗВА» (визначаємо регуляркою NUM_HEAD), або рубрика;
         8.0 — колонтитул, відсіюється раніше у skip_block().
    """
    font, size = dominant(lines[0])
    t0 = lines[0]["txt"].strip()
    allfonts = set()
    for l in lines:
        allfonts |= {x[0] for x in l["fonts"]}
    alltext = " ".join(l["txt"] for l in lines).strip()
    if regime == "digital":
        return _role_digital(lines, font, size, t0)
    if font.startswith("Rodeo"):
        return "chapter_title"
    # Рядок, що починається з маркера списку, — ніколи не заголовок.
    if leading_bullet(lines[0]) is not None or glyph_only(lines[0]):
        return "body"
    if regime == "school":
        if font.startswith("AvantGarde"):
            if size >= PROF["ag_intro"]:
                return "intro"
            if size >= PROF["ag_point"] and NUM_HEAD.match(t0):
                return "point"
            if size >= PROF["ag_sub"]:
                return "sub"
            return "point" if NUM_HEAD.match(t0) else "rubric"
        if font.startswith("Arial-BoldMT") and size >= 12:
            return "sub"
    else:
        if font.startswith("TimesNewRomanPS-Bold") and "Italic" not in font:
            if size >= 15.5 or CHAPTER_HEAD.match(t0):
                return "chapter_plain"
            if NUM_HEAD.match(t0):
                return "point"
            if len(alltext) <= 45 and all(("Bold" in x or x in ("SymbolMT", "Calibri")) for x in allfonts):
                return "letter" if len(alltext) <= 3 else "rubric"
        # Підзаголовок у Word-верстці — це блок, ЦІЛКОМ набраний напівжирним курсивом.
        # Якщо курсивом виділено лише частину рядка, це звичайний текст.
        if font.startswith("TimesNewRomanPS-BoldItalic") and len(alltext) <= 90 \
                and all(x.startswith("TimesNewRomanPS-BoldItalic") or is_bullet_font(x)
                        for x in allfonts):
            return "rubric" if alltext.endswith(":") else "sub"
    if t0.startswith("Мал."):
        return "caption"
    if font.startswith("SchoolBook_Alx-Italic") and size < 10.5:
        return "table_caption"
    return "body"

def head_tail(lines, regime):
    """Відділяє рядок-рубрику від тексту, що йде за ним у тому ж блоці."""
    head = []
    for i, l in enumerate(lines):
        f, sz = dominant(l)
        if (regime == "school" and f.startswith("AvantGarde")) or \
           (regime == "digital" and f.startswith(DG_HEAD + DG_RUBRIC) and sz >= 12.5) or \
           (regime == "times" and f.startswith("TimesNewRomanPS-Bold")):
            head.append(l)
        else:
            return head, lines[i:]
    return head, []

def skip_block(lines, bbox, imgs, page, pno, regime="school"):
    """Чи викинути блок як службовий. Порядок перевірок: від найнадійніших до евристичних.

    Найтонше місце — останні дві перевірки: підписи ВСЕРЕДИНІ схем набрано тим самим Arial 9.5,
    що й текст рубрик, тож розрізняємо їх геометрично (блок накривається невеликим зображенням)
    або за шрифтом (ArialNarrow вживається лише у схемах). Великі фонові зображення шмуцтитулів
    свідомо ігноруємо порогом 8 % площі сторінки — інакше під ніж потрапляв би справжній текст.
    """
    txt = " ".join(l["txt"] for l in lines).strip()
    fonts = set()
    for l in lines:
        fonts |= l["fonts"]
    fnames = {f[0] for f in fonts}
    if not txt or not re.search(r"[\w\u0400-\u04FF]", txt) or len(txt) < 2:
        return True
    if re.fullmatch(r"\d{1,3}", txt) and fnames <= {"ArialMT", "Arial", "TimesNewRomanPSMT"}:
        return True
    if any(f[0].startswith("AvantGarde") and f[1] <= 8.5 for f in fonts):
        return True
    if fnames <= {"CourierNewPS-BoldMT"}:
        return True
    if regime == "digital":
        # колонцифра внизу сторінки
        if re.fullmatch(r"\d{1,3}", txt) and fnames <= {"MyriadPro-Regular"}:
            return True
        return False
    if pno == 3:
        return False
    if regime == "times":
        real = {f for f in fonts if not is_bullet_font(f[0])}
        if real and not any(f[0].startswith("TimesNewRoman") for f in real) \
                and not txt.startswith("Мал.") and len(txt) < 80:
            return True
    if fnames <= {"ArialNarrow", "ArialNarrow-Bold"} and len(txt) < 70:
        return True
    if fnames <= {"Arial-BoldMT", "ArialNarrow", "ArialNarrow-Bold", "Arial-BoldItalicMT", "ArialMT",
                  "Arial-ItalicMT"} and len(txt) < 60 and not txt.endswith(":") \
            and not txt.startswith("Мал.") and not re.match(r"^[" + re.escape(BULLET_CHARS) + r"]", txt) \
            and any(f[1] <= 9.6 for f in fonts):
        if "ArialMT" not in fnames and len(imgs) >= 5:
            return True
        x0, y0, x1, y1 = bbox
        area = max(1.0, (x1 - x0) * (y1 - y0))
        parea = page.rect.width * page.rect.height
        for ix0, iy0, ix1, iy1 in imgs:
            if (ix1 - ix0) * (iy1 - iy0) > 0.08 * parea:
                continue
            ox = min(x1, ix1 + 8) - max(x0, ix0 - 8)
            oy = min(y1, iy1 + 8) - max(y0, iy0 - 8)
            if ox > 0 and oy > 0 and ox * oy > 0.55 * area:
                return True
    return False

def reading_order(items, body_left, body_right):
    """Порядок читання для журнальної верстки 5 класу.

    Сортування «зверху вниз, зліва направо» тут не працює: пояснення до скриншотів
    стоять кількома паралельними колонками, і рядок за рядком вони перемішуються
    («Кнопка Пуск За допомогою цієї» + «Закріпити на Панель швидкого»).
    Тому блок на всю ширину (або заголовок) вважаємо роздільником смуги, а всередині
    смуги блоки збираємо в колонки за перекриттям по X і читаємо колонка за колонкою.
    """
    width = max(1.0, body_right - body_left)
    items = sorted(items, key=lambda it: (round(it.y / 4), it.x0))
    wide = {id(it) for it in items if (it.right - it.left) > 0.55 * width}
    seps = set(wide) | {id(it) for it in items
                        if it.kind in ("chapter_title", "chapter_plain", "point", "sub")}
    # «БЕРЕЖІТЬ СЕБЕ» — вузький заголовок над широким абзацом: якщо його не зробити
    # роздільником, він поїде в колонку й відірветься від свого тексту. А от рубрики
    # на шмуцтитулі («У цьому розділі ви дізнаєтесь:») стоять усередині колонок —
    # їх чіпати не можна, тому дивимось, що йде одразу під рубрикою.
    for a, b in zip(items, items[1:]):
        if a.kind == "rubric" and id(b) in wide and 0 <= b.y - a.y < 45:
            seps.add(id(a))
    out, band = [], []

    def flush():
        cols = []
        for it in sorted(band, key=lambda t: (t.left, t.y)):
            for c in cols:
                over = min(c["r"], it.right) - max(c["l"], it.left)
                if over > 0.45 * min(c["r"] - c["l"], max(1.0, it.right - it.left)):
                    c["items"].append(it)
                    c["l"] = min(c["l"], it.left)
                    c["r"] = max(c["r"], it.right)
                    break
            else:
                cols.append({"l": it.left, "r": it.right, "items": [it]})
        for c in sorted(cols, key=lambda c: c["l"]):
            out.extend(sorted(c["items"], key=lambda t: t.y))
        band.clear()

    for it in items:
        if id(it) in seps:
            flush()
            out.append(it)
        else:
            band.append(it)
    flush()
    return out

# ------------------------------------------------------------------ сторінка
class Item:
    def __init__(self, kind, y, x0, **kw):
        self.kind, self.y, self.x0 = kind, y, x0
        self.__dict__.update(kw)

def process_page(page, pno):
    if PROF["layout"] == "digital":
        regime = "digital"
    else:
        regime = "times" if (PROF["allow_times"] and page.rect.width > 500) else "school"
    d = page_dict(page)
    imgs = [b["bbox"] for b in d["blocks"] if b["type"] != 0]
    text_blocks = merge_split_blocks(d["blocks"])
    tables = []
    try:
        with contextlib.redirect_stdout(sys.stderr):
            found = page.find_tables().tables
        for t in found:
            rows = good_table(t)
            if rows:
                tables.append((t.bbox, rows))
    except Exception:
        pass

    prepared = []
    for b in text_blocks:
        lines = visual_lines(b)
        if not lines or skip_block(lines, b["bbox"], imgs, page, pno, regime):
            continue
        chunks, cur = [], []
        for ln in lines:
            if regime == "times" and re.fullmatch(r"[А-ЯЇІЄҐA-Z]", ln["txt"].strip()):
                if cur:
                    chunks.append(cur)
                chunks.append([ln]); cur = []
            else:
                cur.append(ln)
        if cur:
            chunks.append(cur)
        if len(chunks) > 1:
            for ch in chunks:
                bb = (min(l["x0"] for l in ch), min(l["y"] for l in ch),
                      max(l["x1"] for l in ch), max(l["y"] for l in ch) + 12)
                prepared.append((dict(b, bbox=bb), ch))
            continue
        x0, y0, x1, y1 = b["bbox"]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if any(tx0 - 2 <= cx <= tx1 + 2 and ty0 - 2 <= cy <= ty1 + 2 for (tx0, ty0, tx1, ty1), _ in tables):
            continue
        prepared.append((b, lines))

    if prepared:
        body_left = min(b["bbox"][0] for b, _ in prepared)
        body_right = max(b["bbox"][2] for b, _ in prepared)
    else:
        body_left, body_right = 37.0, 423.0
    bodywidth = body_right - body_left

    items = []
    for b, lines in prepared:
        x0, y0, x1, y1 = b["bbox"]
        side = False
        if regime != "digital" and (x1 - x0) < 0.5 * bodywidth:
            for ob, _ in prepared:
                if ob is b:
                    continue
                ox0, oy0, ox1, oy1 = ob["bbox"]
                if min(y1, oy1) - max(y0, oy0) > 12 and (ox1 < x0 + 3 or ox0 > x1 - 3) \
                        and (ox1 - ox0) > 0.35 * bodywidth:
                    side = True
                    break
        role = role_of(lines, regime, pno)
        items.append(Item(role, y0, x0, lines=lines, side=side,
                          left=x0, right=x1, regime=regime))
    for bbox, rows in tables:
        items.append(Item("table", bbox[1], bbox[0], rows=rows, side=False,
                          left=bbox[0], right=bbox[2]))
    if regime == "digital":
        items = reading_order(items, body_left, body_right)
    else:
        items.sort(key=lambda it: (round(it.y / 4), it.x0))
    return items, body_left, body_right, bodywidth, regime

# ------------------------------------------------------------------ вивід
def join_lines_text(lines):
    acc, raw = "", ""
    for l in lines:
        piece = l["txt"].strip()
        if not acc:
            acc = piece
        else:
            mode = join_mode(raw, piece)
            tail = acc.rstrip()
            if mode == "soft":
                acc = (tail[:-1] if tail.endswith("\xad") else tail) + piece
            elif mode == "strip":
                acc = (tail[:-1] if tail.endswith("-") else tail) + piece
            elif mode == "tight":
                acc = tail + piece
            else:
                acc = tail + " " + piece
        raw = l["raw"]
    return re.sub(r"\s+", " ", acc).strip()

LEADER = re.compile(r"(?:\.\s*){3,}")

def render_toc(items):
    """Сторінки змісту: кожен запис — окремий пункт списку."""
    out, buf, raw = [], [], ""
    def flush():
        nonlocal buf, raw
        if buf:
            t = re.sub(r"\s+", " ", "".join(buf)).strip()
            t = LEADER.sub(" … ", t)
            t = re.sub(r"\s*…\s*(\d{1,3})$", r" — с. \1", t)
            t = re.sub(r"^(\d+)\.\s+(\d+)\.", r"\1.\2.", t)
            if t:
                out.append("- " + t)
        buf, raw = [], ""
    for it in items:
        if it.kind == "table":
            continue
        for ln in it.lines:
            txt = ln["txt"].strip()
            if not txt:
                continue
            if any(f[0].startswith("Arial-Bold") and f[1] >= 12 for f in ln["fonts"]):
                flush()
                if not any(x.startswith("## ") for x in out):
                    out += ["", "## Зміст", ""]
                continue
            if any(f[0] == "SchoolBook_Alx-Bold" and f[1] >= 11.5 for f in ln["fonts"]):
                flush()
                out += ["", f"**{txt}**", ""]
                continue
            if buf:
                buf.append("" if is_hyphen_break(raw) else " ")
            buf.append(txt)
            raw = ln["raw"]
            if re.search(r"\d{1,3}\s*$", txt) and LEADER.search(txt):
                flush()
    flush()
    return [""] + out + [""]

def emit(items, body_left, body_right, bodywidth, chapter_no, regime):
    flow = {"times": "full", "digital": "digital"}.get(regime, "indent")
    body_lines = [l for it in items if it.kind != "table" for l in it.lines]
    if sum(1 for l in body_lines if LEADER.search(l["txt"])) >= 5:
        return render_toc(items)
    out = []
    i = 0
    while i < len(items):
        it = items[i]
        pre = "> " if (it.side and it.kind == "body") else ""
        if it.kind == "table":
            out += [""] + table_md(it.rows) + [""]
            i += 1
            continue
        lines = it.lines
        if it.kind == "chapter_title":
            t = join_lines_text(lines)
            j = i + 1
            while j < len(items) and items[j].kind == "chapter_title":
                t += " " + join_lines_text(items[j].lines); j += 1
            num = f"Розділ {chapter_no}. " if chapter_no else ""
            out += ["", f"## {num}{re.sub(r'\s+', ' ', t).strip()}", ""]
            i = j
            continue
        if it.kind == "chapter_plain":
            out += ["", f"## {join_lines_text(lines)}", ""]; i += 1; continue
        if it.kind == "point":
            t = join_lines_text(lines)
            j = i + 1
            while j < len(items) and items[j].kind == "point" and items[j].y - items[j - 1].y < 18:
                t += " " + join_lines_text(items[j].lines); j += 1
            t = re.sub(r"\s+", " ", t).rstrip(".")
            t = re.sub(r"^(Тема)\s*(\d+)\s*", r"\1 \2. ", t)
            out += ["", f"### {t}", ""]; i = j; continue
        if it.kind in ("sub", "intro", "letter"):
            head, tail = head_tail(lines, it.regime) if it.kind != "letter" else (lines, [])
            if not head:
                head, tail = lines, []
            level = "###" if it.kind == "letter" else "####"
            t = join_lines_text(head)
            j = i + 1
            if it.kind == "sub" and not tail:
                while j < len(items) and items[j].kind == "sub" and items[j].y - items[j - 1].y < 18:
                    t += " " + join_lines_text(items[j].lines); j += 1
            out += ["", f"{level} {re.sub(r'\s+', ' ', t).strip()}", ""]
            if tail:
                out += render_flat(tail, pre)
            i = j
            continue
        if it.kind == "rubric":
            head, tail = head_tail(lines, it.regime)
            if not head:
                head, tail = lines, []
            t = join_lines_text(head)
            if re.match(r"^Практична робота № ?\d+", t):
                if re.fullmatch(r"Практична робота № ?\d+\.?", t) and i + 1 < len(items) \
                        and items[i + 1].kind == "rubric" \
                        and join_lines_text(items[i + 1].lines).startswith("«"):
                    t = t.rstrip(".") + ". " + join_lines_text(items[i + 1].lines)
                    i += 1
                out += ["", f"#### {t}", ""]
                if tail:
                    out += render_flat(tail, pre)
                i += 1
                continue
            out += ["", f"**{t}**", ""]
            if tail:
                out += render_flat(tail, pre)
            i += 1
            continue
        if it.kind in ("caption", "table_caption"):
            t = join_lines_text(lines)
            j = i + 1
            while j < len(items) and it.kind == "caption" and items[j].kind == "body" \
                    and items[j].y - it.y < 24 \
                    and len(join_lines_text(items[j].lines)) < 70 \
                    and all(f[0].startswith(("ArialMT", "Arial-Italic")) for l in items[j].lines for f in l["fonts"]):
                t += " " + join_lines_text(items[j].lines)
                j += 1
            out += ["", f"*{re.sub(r'\s+', ' ', t).strip()}*", ""]
            i = j
            continue
        # body: збираємо підряд усі сусідні body-блоки з тим самим статусом
        wide = flow == "full"
        if wide:
            groups = [(body_left, body_right, it.lines)]
        else:
            groups = [(it.left, it.right, it.lines)]
        j = i + 1
        while j < len(items) and items[j].kind == "body" and items[j].side == it.side:
            if flow == "digital" and (items[j].left > it.right or items[j].right < it.left):
                break          # сусідній блок — з іншої колонки, а не продовження абзацу
            if wide:
                groups.append((body_left, body_right, items[j].lines))
            else:
                groups.append((items[j].left, items[j].right, items[j].lines))
            j += 1
        out += render_md(groups, body_left, bodywidth, pre, flow)
        i = j
    return out


def render_flat(lines, pre):
    """Текст рубрики: суцільний абзац; питання, розділені ●, стають списком."""
    runs, raw = [], ""
    for ln in lines:
        r = line_runs(ln["spans"], keep_bullets=True)
        if not runs:
            runs = [list(x) for x in r]
        else:
            runs = merge_runs(runs, raw, r)
        raw = ln["raw"]
    md = runs_md(runs).strip()
    if not md:
        return []
    parts = [x.strip() for x in re.split(r"\s*[●•]\s*", md) if x.strip()]
    if len(parts) > 1:
        return [""] + [pre + "- " + x for x in parts] + [""]
    md = parts[0]
    if re.match(r"^\*{0,3}\d{1,2}\*{0,3}\.\s", md):
        chunks = re.split(r"(?:(?<=\s)|^)\*{0,3}(\d{1,2})\*{0,3}\.\s+", md)
        pairs = [(chunks[k], chunks[k + 1].strip()) for k in range(1, len(chunks) - 1, 2)]
        if len(pairs) > 1:
            return [""] + [pre + f"{n}. {t}" for n, t in pairs if t] + [""]
    return ["", pre + md, ""]

def render_md(groups, body_left, bodywidth, pre, flow="indent"):
    out = []
    for kind, payload in render_stream(groups, body_left, bodywidth, flow):
        if kind == "p":
            out += ["", pre + payload, ""]
        elif kind == "code":
            out += ["", pre + "```python"] + [pre + c for c in payload] + [pre + "```", ""]
        elif kind == "ul":
            out.append("")
            for lvl, text, num in payload:
                marker = f"{num}. " if num is not None else "- "
                out.append(pre + "  " * lvl + marker + text.strip())
            out.append("")
    return out

CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

def tidy(lines):
    """Прибирає порожні рядки поспіль і службові символи.

    \x07 — «невидимий» маркер Symbol; там, де він правив за маркер списку, його вже
    перетворено на «- », а решта (напр. у назвах розділів 5 класу) — сміття верстки.
    Чистимо саме тут, після розбору списків, щоб не зламати leading_bullet().
    """
    res = []
    for ln in lines:
        ln = CTRL.sub("", ln).rstrip()
        if not ln.strip() and res and not res[-1].strip():
            continue
        res.append(ln)
    while res and not res[0].strip():
        res.pop(0)
    return res

def main():
    ap = argparse.ArgumentParser(description="PDF-підручник -> Markdown")
    ap.add_argument("pdf", help="шлях до PDF")
    ap.add_argument("--out", help="куди записати .md (без нього — у stdout)")
    ap.add_argument("--title", default="", help="заголовок H1, напр. \"Інформатика. 9 клас\"")
    ap.add_argument("--source", default="", help="шлях до PDF для примітки у шапці")
    ap.add_argument("--no-page-marks", action="store_true",
                    help="не вставляти коментарі <!-- с. N -->")
    ap.add_argument("--profile", choices=sorted(PROFILES), default=None,
                    help="профіль верстки (клас). Без нього визначається з імені файлу")
    args = ap.parse_args()

    global PROF
    prof = args.profile
    if prof is None:
        m = re.search(r"(\d)\s*-?\s*клас", args.pdf)
        prof = m.group(1) if m and m.group(1) in PROFILES else "9"
        print(f"Профіль: {prof} (визначено з імені файлу)", file=sys.stderr)
    PROF = PROFILES[prof]

    doc = pymupdf.open(args.pdf)
    all_lines = []
    for pno in range(doc.page_count):
        page = doc[pno]
        newchap = None
        for b in page_dict(page)["blocks"]:
            if b["type"] != 0:
                continue
            for l in b["lines"]:
                for s in l["spans"]:
                    if s["font"] == "CourierNewPS-BoldMT" and s["size"] > 30 and s["text"].strip().isdigit():
                        newchap = int(s["text"].strip())
        items, body_left, body_right, bodywidth, regime = process_page(page, pno)
        md = emit(items, body_left, body_right, bodywidth, newchap, regime)
        if any(x.strip() for x in md):
            # Номер друкованої сторінки в цих книжках збігається з індексом сторінки PDF.
            if not args.no_page_marks:
                all_lines.append(f"<!-- с. {pno + PROF['page_offset']} -->")
            all_lines += md
    header = []
    if args.title:
        src = args.source or args.pdf
        header = [
            f"# {args.title}",
            "",
            "> Markdown-версія підручника, згенерована з PDF автоматичним конвертером. "
            "Ілюстрації не перенесено — збережено лише підписи до них; схеми, окремі таблиці "
            "та формули спрощено. Коментарі виду `<!-- с. 12 -->` позначають сторінку "
            f"оригіналу; для точних формулювань і завдань звіряйтеся з `{src}`.",
            "",
        ]
    text = "\n".join(header + tidy(all_lines)) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Записано: {args.out} ({len(text.splitlines())} рядків)", file=sys.stderr)
    else:
        sys.stdout.write(text)

if __name__ == "__main__":
    main()
