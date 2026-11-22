"""Готові покрокові скріни Google Документів для колод 5–6 класу. Номери на скрінах = номери кроків на слайді."""
from gdocs import Doc, INSERT, IMAGE_SUB, BREAK_SUB, FILE, DOWNLOAD_SUB, TABLE_CTX, WRAP
import gdocs_spravzhni as R

# Спершу беремо СПРАВЖНІЙ скрін Google Документів (gdocs_spravzhni.py, знято в Chrome учителя з українським
# інтерфейсом). Намальований у HTML (Doc нижче) — лише запасний варіант, якщо справжнього для цього випадку ще немає.
REAL_LISTS = {("bullet", "рюкзак"): "list-bullet-pokhid", ("number", "Збір о 8:00 біля школи"): "list-number-pokhid",
              ("bullet", "два яйця"): "list-bullet-mlyntsi", ("number", "Збити яйця з цукром"): "list-number-mlyntsi"}


def _real(key, nums):
    return R.real(key, nums) if key in R.SHOT else None



def _n(nums, i):
    """Номер позначки: за замовчуванням 1, 2, 3…; nums=(3, 3, 3) — усе це крок 3; None у списку — рамка без номера."""
    if nums is None:
        return i + 1
    if nums is False:
        return None
    return nums[i]


HAMSTER_TEXT = ("Хом’як — один із найпростіших домашніх улюбленців. Йому потрібна клітка з колесом, бо вночі він багато "
                "бігає. Годують хом’яка зерном, свіжою морквою і яблуком, а солодке й солоне йому давати не можна.")
CLUBS_HEAD = ["День", "Гурток", "Час", "Кабінет"]
CLUBS = [["Понеділок", "футбол", "16:00", "спортзал"], ["Вівторок", "музика", "15:00", "12"],
         ["Середа", "футбол", "16:00", "спортзал"], ["Четвер", "англійська", "17:00", "8"],
         ["П’ятниця", "малювання", "15:00", "5"]]


def insert_table(cols=4, rows=6, title="Гуртки — Прізвище", heading="Розклад гуртків", nums=None):
    """Вставити → Таблиця → обводимо сітку."""
    if (cols, rows) in ((4, 6), (3, 5)):
        return _real(f"tabl{cols}x{rows}", nums)
    g = Doc(title=title)
    g.page(g.p(heading, bold=True, size=16) + g.p("", caret=True))
    g.menu_bar_open("Вставити", INSERT, sub="Таблиця", sub_html=Doc.table_grid(cols, rows))
    g.mark("[data-top='Вставити']", _n(nums, 0), side="top")
    g.mark("#dd-main [data-item='Таблиця']", _n(nums, 1), side="left")
    g.mark("#tgrid .c.on", _n(nums, 2), pad=3, side="bottom")
    return g.shot(f"tabl{cols}x{rows}", crop=["[data-top='Вставити']", "#dd-sub"], pad=10)


def table_row_below(rows=None, at=(5, 0), nums=None):
    """Права кнопка в рядку п’ятниці → «Вставити рядок нижче»."""
    if rows is None and at == (5, 0):
        return _real("tablrow", nums)
    rows = rows or [CLUBS_HEAD] + CLUBS
    g = Doc(title="Гуртки — Прізвище")
    g.page(g.p("Розклад гуртків", bold=True, size=16)
           + g.table(rows, widths=[150, 150, 90, 120], head_bold=True, caret=at))
    g.context_menu(f"[data-cell='{at[0]}-{at[1]}']", TABLE_CTX, hl="Вставити рядок нижче")
    g.mark(f"[data-cell='{at[0]}-{at[1]}']", _n(nums, 0), side="left", pad=2)
    g.mark("#dd-ctx [data-item='Вставити рядок нижче']", _n(nums, 1), side="right", pad=2)
    return g.shot("tablrow", crop=["#t1", "#dd-ctx [data-item='Видалити таблицю']"], pad=12)


def table_col_right(rows=None, at=(2, 3), nums=None):
    """Права кнопка в стовпці «Кабінет» → «Вставити стовпець справа»."""
    if rows is None:
        return _real("tablcol", nums)
    rows = rows or [CLUBS_HEAD] + CLUBS
    g = Doc(title="Гуртки — Прізвище")
    g.page(g.p("Розклад гуртків", bold=True, size=16)
           + g.table(rows, widths=[150, 150, 90, 120], head_bold=True, caret=at))
    g.context_menu(f"[data-cell='{at[0]}-{at[1]}']", TABLE_CTX, hl="Вставити стовпець справа")
    g.mark(f"[data-cell='{at[0]}-{at[1]}']", _n(nums, 0), side="left", pad=2)
    g.mark("#dd-ctx [data-item='Вставити стовпець справа']", _n(nums, 1), side="right", pad=2)
    return g.shot("tablcol", crop=["[data-cell='0-2']", f"[data-cell='{len(rows) - 1}-3']",
                                   "#dd-ctx [data-item='Видалити таблицю']"], pad=12)


def table_head_bold(nums=None):
    """Виділили шапку → B (жирний)."""
    return _real("tablbold", nums)
    g = Doc(title="Гуртки — Прізвище")
    g.on.add("bold")
    g.page(g.p("Розклад гуртків", bold=True, size=16)
           + g.table([CLUBS_HEAD] + CLUBS[:3], widths=[150, 150, 90, 120], head_bold=True,
                     sel={(0, 0), (0, 1), (0, 2), (0, 3)}))
    g.table_tools = True
    g.mark("[data-row='0']", _n(nums, 0), side="left", pad=2)
    g.mark("[data-b='bold']", _n(nums, 1), side="top", pad=3)
    g.mark("[data-b='fill']", _n(nums, 2), side="top", pad=3)
    return g.shot("tablbold", crop=["[data-b='size']", "[data-b='bdash']", "#t1"], pad=12)


def merge_cells(nums=None):
    """Виділили дві клітинки «Понеділок» → права кнопка → «Об’єднати клітинки»."""
    return _real("obyednaty", nums)
    rows = [["<b>День</b>", "<b>Хто чергує</b>", "<b>Що робить</b>"], ["Понеділок", "Коваль", "витирає дошку"],
            ["Понеділок", "Мороз", "поливає квіти"], ["Вівторок", "Ткач", "витирає дошку"]]
    g = Doc(title="Чергування — Прізвище", page_x=420)
    g.page(g.p("Чергування", bold=True, size=16) + g.table(rows, widths=[130, 130, 160], sel={(1, 0), (2, 0)}))
    g.context_menu("[data-cell='2-0']", TABLE_CTX, hl="Об’єднати клітинки", place="at-right")
    g.mark("[data-cell='1-0'], [data-cell='2-0']", _n(nums, 0), side="left", pad=2)
    g.mark("#dd-ctx [data-item='Об’єднати клітинки']", _n(nums, 1), side="right", pad=2)
    return g.shot("obyednaty", crop=["#t1", "#dd-ctx"], pad=12)


def format_toolbar(nums=None):
    """Де на панелі шрифт, розмір, B I U і колір (виділено слово «Кіт»)."""
    return _real("panel-format", nums)
    g = Doc(title="Мій вихідний — Прізвище", page_x=420)
    g.page(g.p("Мій кіт любить спати на підвіконні.".replace("кіт", '<span class="sel">кіт</span>')))
    g.mark("#page .sel", _n(nums, 0), side="bottom", pad=3)
    g.mark("[data-b='font']", _n(nums, 1), side="bottom", pad=3)
    g.mark("[data-b='size']", _n(nums, 2), side="bottom", pad=3)
    g.mark("[data-b='bold'], [data-b='italic'], [data-b='underline']", _n(nums, 3), side="bottom", pad=3)
    g.mark("[data-b='color']", _n(nums, 4), side="bottom", pad=3)
    return g.shot("panel-format", crop=["[data-b='font']", "[data-b='highlight']", "#page .sel"], pad=12)


def page_break(nums=None):
    """Вставити → Розрив → Розрив сторінки."""
    g = Doc(title="Шпаргалка — Прізвище")
    g.page(g.p("Шпаргалка з теми «Текстові документи»", bold=True, size=14) + g.p("", caret=True))
    g.menu_bar_open("Вставити", INSERT, sub="Розрив", sub_items=BREAK_SUB, sub_hl="Розрив сторінки")
    g.mark("[data-top='Вставити']", _n(nums, 0), side="top")
    g.mark("#dd-main [data-item='Розрив']", _n(nums, 1), side="left")
    g.mark("#dd-sub [data-item='Розрив сторінки']", _n(nums, 2), side="bottom", pad=2)
    return g.shot("rozryv", crop=["[data-top='Вставити']", "#dd-main [data-item='Закладка']", "#dd-sub"], pad=10)


def insert_image_web(title="Хом’як — Прізвище", heading="Хом’як удома", text=HAMSTER_TEXT, nums=None):
    """Вставити → Зображення → Шукати в Інтернеті."""
    return _real("zobr-autumn" if "Ярмарок" in title else "zobr", nums)
    g = Doc(title=title)
    g.page(g.p(heading, bold=True, size=20, align="center") + g.p('<span class="caret"></span>' + text))
    g.menu_bar_open("Вставити", INSERT, sub="Зображення", sub_items=IMAGE_SUB, sub_hl="Шукати в Інтернеті")
    g.mark("[data-top='Вставити']", _n(nums, 0), side="top")
    g.mark("#dd-main [data-item='Зображення']", _n(nums, 1), side="left")
    g.mark("#dd-sub [data-item='Шукати в Інтернеті']", _n(nums, 2), side="bottom", pad=2)
    return g.shot("zobr", crop=["[data-top='Вставити']", "#dd-sub"], pad=10)


def image_corner(art="hamster", title="Хом’як — Прізвище", nums=None):
    """Клацнули по фото — маркери; тягнемо за кутовий."""
    g = Doc(title=title)
    g.page(g.p("Хом’як удома", bold=True, size=20, align="center")
           + g.p(g.image(art, 300, 225, selected=True)) + g.p(HAMSTER_TEXT))
    g.mark("#img1 svg", _n(nums, 0), side="left", pad=4)
    g.mark("[data-h='corner-7']", _n(nums, 1), side="right", pad=6, cursor=True)
    return g.shot("kut", crop=["#img1"], pad=46)


def image_selected(art="hamster", w=300, h=225):
    """Просто виділене фото з маркерами — без позначок."""
    if art == "hamster":
        return _real("vydil-hamster", False)
    g = Doc(title="Хом’як — Прізвище")
    g.page(g.p(g.image(art, w, h, selected=True)) + g.p(HAMSTER_TEXT))
    return g.shot(f"vydil-{art}", crop=["#img1"], pad=34)


def wrap_bar(on="wrap", tip="wrap", art="hamster", title="Хом’як — Прізвище", mode=None, text=HAMSTER_TEXT, nums=None):
    """Клацнули по фото — під ним панель обтікання; позначено потрібну кнопку."""
    if on == "wrap" and tip == "wrap":
        return _real("wrap-autumn" if art == "landscape" else "wrap-hamster", nums)
    mode = mode or {"inline": "inline", "wrap": "wrap", "break": "break"}.get(on, "wrap")
    g = Doc(title=title, page_w=640)
    img = g.image(art, 200, 150, selected=True, mode=mode, wrapbar=True, wrap_on=on)
    g.page(g.p(img + text))
    label = dict(WRAP)[tip]
    g.tooltip(f"[data-wrap='{tip}']", label)
    g.mark("#img1 svg", _n(nums, 0), side="left", pad=6)
    g.mark(f"[data-wrap='{tip}']", _n(nums, 1), side="top", pad=2)
    return g.shot(f"wrap-{on}-{tip}", crop=["#img1", "#wrapbar", ".tip", "#page p"], pad=8)


def lists(kind="bullet", items=("рюкзак", "спальник", "ліхтарик", "вода"), nums=None):
    """Виділили рядки → кнопка «Маркований» або «Нумерований список»."""
    key = REAL_LISTS.get((kind, items[0]))
    if key:
        return _real(key, nums)
    g = Doc(title="Похід — Прізвище", page_x=760)
    g.on.add(kind)
    body = "".join(g.p(t, sel=True) for t in items)
    head = {"bullet": "Що взяти з собою", "number": "Як пройде день"}[kind]
    g.page(g.p(head, bold=True, size=14) + body)
    name = {"bullet": "Маркований список (Ctrl+Shift+8)", "number": "Нумерований список (Ctrl+Shift+7)"}[kind]
    g.tooltip(f"[data-b='{kind}']", name)
    g.mark("#page .sel", _n(nums, 0), side="left", pad=4)
    g.mark(f"[data-b='{kind}']", _n(nums, 1), side="top", pad=3)
    return g.shot(f"list-{kind}", crop=["[data-b='align']", "[data-b='clear']", "#page .sel", ".tip"], pad=12)


def align(which="format_align_center", nums=None):
    """Кнопка вирівнювання → вибираємо варіант."""
    if which == "format_align_center":
        return _real("align-center", nums)
    from gdocs import ALIGN
    g = Doc(title="Оголошення — Прізвище", page_x=700)
    g.page(g.p("Оголошення", bold=True, size=20, sel=True) + g.p("У суботу о 10:00 у шкільному дворі — толока."))
    g.button_menu("align", Doc.align_menu(which))
    name = {k: f"{n} ({kb})" for k, n, kb in ALIGN}[which]
    g.tooltip(f"[data-al='{which}']", name)
    g.mark("#page .sel", _n(nums, 0), side="left", pad=4)
    g.mark("[data-b='align']", _n(nums, 1), side="top", pad=3)
    g.mark(f"[data-al='{which}']", _n(nums, 2), side="right", pad=2)
    return g.shot(f"align-{which}", crop=["[data-b='align']", "#dd-btn", ".tip", "#page .sel"], pad=12)


def font_size(size=20, nums=None):
    """Виділили заголовок → розмір у полі між «−» і «+» → B → по центру."""
    if size == 20:
        return _real("shryft20", nums)
    g = Doc(title="Хом’як — Прізвище", size=size, page_x=380)
    g.on.update({"bold"})
    g.page(g.p("Хом’як удома", bold=True, size=size, sel=True) + g.p(HAMSTER_TEXT))
    g.mark("#page .sel", _n(nums, 0), side="left", pad=4)
    g.mark("[data-b='size'] .v", _n(nums, 1), side="bottom", pad=3)
    g.mark("[data-b='bold']", _n(nums, 2), side="bottom", pad=3)
    g.mark("[data-b='align']", _n(nums, 3), side="bottom", pad=3)
    return g.shot(f"shryft{size}", crop=["[data-b='font']", "[data-b='align']", "#page .sel"], pad=12)


def line_spacing(on="1,5", nums=None):
    if on == "1,5":
        return _real("interval1,5", nums)
    g = Doc(title="Заява — Прізвище", page_x=560)
    g.page(g.p("Прошу дозволити мені взяти участь", sel=True) + g.p("у шкільній виставці малюнків.", sel=True))
    g.button_menu("spacing", Doc.spacing_menu(on), min_w=180)
    g.mark("#page .sel", _n(nums, 0), side="left", pad=4)
    g.mark("[data-b='spacing']", _n(nums, 1), side="top", pad=3)
    g.mark(f"#dd-btn [data-item='{on}']", _n(nums, 2), side="right", pad=2)
    return g.shot(f"interval{on}", crop=["[data-b='spacing']", "#dd-btn [data-item='Подвійний']",
                                          "#page .sel"], pad=12)


def page_setup(orient="landscape", nums=None):
    """Файл → Налаштування сторінки → Альбомна → OK."""
    if orient == "landscape":
        return _real("nalasht-landscape", nums)
    g = Doc(title="Розклад — Прізвище")
    g.page(g.p("Розклад уроків", bold=True, size=16))
    g.page_setup(orient)
    g.mark("#or-" + orient, _n(nums, 0), side="left", pad=4)
    g.mark("#ps-ok", _n(nums, 1), side="bottom", pad=3)
    return g.shot(f"nalasht-{orient}", crop=["#psetup"], pad=40)


def file_page_setup(nums=None):
    """Файл → Налаштування сторінки (саме меню)."""
    return _real("file-nalasht", nums)
    g = Doc(title="Розклад — Прізвище")
    g.page(g.p("Розклад уроків", bold=True, size=16))
    g.menu_bar_open("Файл", FILE, hl="Налаштування сторінки")
    g.mark("[data-top='Файл']", _n(nums, 0), side="top")
    g.mark("#dd-main [data-item='Налаштування сторінки']", _n(nums, 1), side="right", pad=2)
    return g.shot("file-nalasht", crop=["[data-top='Файл']", "#dd-main"], pad=12)


def download_pdf(nums=None):
    """Файл → Завантажити → Документ PDF (.pdf)."""
    return _real("pdf", nums)
    g = Doc(title="Шпаргалка — Прізвище")
    g.page(g.p("Шпаргалка з теми «Текстові документи»", bold=True, size=14))
    g.menu_bar_open("Файл", FILE, sub="Завантажити", sub_items=DOWNLOAD_SUB, sub_hl="Документ PDF (.pdf)")
    g.mark("[data-top='Файл']", _n(nums, 0), side="top")
    g.mark("#dd-main [data-item='Завантажити']", _n(nums, 1), side="left")
    g.mark("#dd-sub [data-item='Документ PDF (.pdf)']", _n(nums, 2), side="right", pad=2)
    return g.shot("pdf", crop=["[data-top='Файл']", "#dd-main [data-item='Перемістити в кошик']", "#dd-sub"], pad=10)


if __name__ == "__main__":
    for f in [merge_cells, format_toolbar, insert_table, table_row_below, table_col_right, table_head_bold, page_break, insert_image_web,
              image_corner, wrap_bar, lists, align, font_size, line_spacing, page_setup, file_page_setup, download_pdf]:
        print(f.__name__, f())


# ---------- готові слайди, що повторюються в колодах 5 і 6 класу ----------
def slide_wrap(d, keys, ours, notes, art="hamster", title="Де це в Google Документах", text=HAMSTER_TEXT):
    """Слайд «Де це в Google Документах»: справжній скрін меню обтікання під фото + розшифровка значків.
    keys — які кнопки пояснюємо (з WRAP), ours — як ці варіанти звуться на уроці."""
    from gdocs import wrap_icon
    from deck import INK2
    s = d.slide(title, notes)
    s.h2(title)
    s.gsteps(["Клацніть по фото.", "Під фото — кнопка з трикутником <b>▾</b>.", "Виберіть, як стоїть фото."],
             x=128, y=200, w=900, size=28, gap=10)
    s.gshot(128, 380, 900, wrap_bar("wrap", "wrap", art=art, text=text), maxh=640)
    labels = dict(WRAP)
    hh = 166 if len(keys) <= 3 else 140
    for k, key in enumerate(keys):
        with s.frame():
            y = 230 + k * (hh + 20)
            s.box(1090, y, 702, hh, "blue" if key == "wrap" else "light")
            s.raw(f'<div style="position:absolute;left:1114px;top:{y + (hh - 92) / 2}px;width:92px;height:92px;'
                  f'background:#FFFFFF;border-radius:12px;display:flex;align-items:center;justify-content:center">'
                  f'{wrap_icon(key, 76)}</div>')
            s.text(1230, y + 10, 546, hh - 20, [f"<b>{labels[key]}</b>", f"у нас — «{ours[key]}»"], size=28,
                   valign="center")
    rest = [labels[k].lower() for k, _ in WRAP if k not in keys]
    if rest:
        with s.frame():
            y = 230 + len(keys) * (hh + 20) + 10
            s.text(1090, y, 702, 90, "Ще " + " і ".join(f"<b>{r}</b>" for r in rest) + " — поки не чіпаємо.", size=26,
                   color=INK2)
    return s
