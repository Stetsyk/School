"""Скриншоти Google Документів для колод про текстові документи (5–6 клас).

Справжні Google Документи з робочого середовища недоступні, тому інтерфейс відтворено в HTML за справжнім
скрінами вчителя (Mac, Chrome, український інтерфейс, листопад 2026; лежать у Tools/slides/gdocs-zrazky): ті самі меню («Файл · Змінити · Вигляд ·
Вставити · Формат · Інструменти · Розширення · Довідка»), панель-«пігулка», значки Material Symbols (шрифт
значків Google) і шрифт Google Sans. Назви пунктів меню звірено з довідкою Google українською.
Рендерить справжній Chrome (Playwright), тому вигляд — як у браузері.

Використання:
    g = Doc(title="Гуртки — Коваль")
    g.page(g.p("Розклад гуртків", bold=True) + g.table(...))
    g.menu_bar_open("Вставити", INSERT, hl="Таблиця", sub=g.table_grid(4, 6))
    g.mark("[data-top='Вставити']", 1)
    g.mark("[data-item='Таблиця']", 2)
    png = g.shot("klas5_tabl", crop=["[data-top='Вставити']", ".dd"])

Позначки на скріні: помаранчева рамка + кружечок із номером кроку (той самий номер — у кроках на слайді).

Що звірено (скріни вчителя в gdocs-zrazky/ або довідка Google українською): верхнє меню, панель, меню «Вставити» і
сітка таблиці, «Вставити → Таблиця», «Формат → Таблиця → Параметри таблиці», контекстне меню таблиці (вставити/видалити
рядок і стовпець, вирівняти, об’єднати, сортувати), «Файл → Налаштування сторінки» (Орієнтація, Розмір паперу, Колір
сторінки, «Використовувати за умовчанням»), «Формат → Маркери й нумерація», «Вставити → Розрив», назви кнопок
вирівнювання й списків із клавішами.
Ще НЕ звірено (найкраще припущення — виправити, коли вчитель надішле скрін): підменю «Зображення», назви кнопок
обтікання (WRAP), решта меню «Файл» і «Формат», підписи полів у вікні налаштування сторінки, меню інтервалів,
відерце заливки на панелі, підменю «Малюнок».
"""
import hashlib
import json
import os
import subprocess

from deck import SHOT_CACHE

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(SHOT_CACHE, "gdocs-fonts")
MARK = "#F2711C"   # помаранчевий — видно і на проєкторі
SEL_BLUE = "#1A73E8"

# ---------- меню (тексти звірено зі скріном і довідкою Google українською) ----------
TOP = ["Файл", "Змінити", "Вигляд", "Вставити", "Формат", "Інструменти", "Розширення", "Довідка"]

# Пункт: (значок, текст, клавіші, є підменю) або "—" (лінія).
INSERT = [("image", "Зображення", "", True), ("table", "Таблиця", "", True), ("note_add", "Шаблони", "", True),
          ("smart_button", "Розумні чіпи", "", True), ("signature", "Електронний підпис", "", False, "Платні функції"),
          ("link", "Посилання", "Ctrl+K", False), ("picture_in_picture", "Малюнок", "", True),
          ("insert_chart", "Діаграма", "", True), ("sentiment_satisfied", "Символи", "", True),
          ("function", "Формула", "", False), "—",
          ("article", "Вкладка", "Shift+F11", False), ("horizontal_rule", "Горизонтальна лінія", "", False),
          ("insert_page_break", "Розрив", "", True), ("bookmark", "Закладка", "", False),
          ("view_agenda", "Елементи сторінки", "", True)]
IMAGE_SUB = [("upload", "Завантажити з комп’ютера", "", False), ("travel_explore", "Пошук в Інтернеті", "", False),
             ("add_to_drive", "Диск", "", False), ("photo_library", "Фото", "", False),
             ("link", "За URL-адресою", "", False), ("photo_camera", "Камера", "", False)]
BREAK_SUB = [("insert_page_break", "Розрив сторінки", "Ctrl+Enter", False),
             ("splitscreen", "Розрив розділу (наступна сторінка)", "", False),
             ("splitscreen_bottom", "Розрив розділу (неперервний)", "", False)]
FILE = [("note_add", "Створити", "", True), ("folder_open", "Відкрити", "Ctrl+O", False),
        ("content_copy", "Створити копію", "", False), "—",
        ("person_add", "Надати доступ", "", True), ("mail", "Електронна пошта", "", True),
        ("download", "Завантажити", "", True), "—",
        ("drive_file_rename_outline", "Перейменувати", "", False), ("drive_file_move", "Перемістити", "", False),
        ("delete", "Перемістити в кошик", "", False), "—",
        ("history", "Історія версій", "", True), "—",
        ("info", "Відомості", "", True), ("language", "Мова", "", True),
        ("description", "Налаштування сторінки", "", False), ("print", "Друк", "Ctrl+P", False)]
DOWNLOAD_SUB = [(None, "Microsoft Word (.docx)", "", False), (None, "Формат OpenDocument (.odt)", "", False),
                (None, "Формат RTF (.rtf)", "", False), (None, "Документ PDF (.pdf)", "", False),
                (None, "Звичайний текст (.txt)", "", False), (None, "Вебсторінка (.html, архів)", "", False),
                (None, "Публікація EPUB (.epub)", "", False), (None, "Markdown (.md)", "", False)]
TABLE_CTX = [("content_cut", "Вирізати", "Ctrl+X", False), ("content_copy", "Копіювати", "Ctrl+C", False),
             ("content_paste", "Вставити", "Ctrl+V", False), "—",
             ("add", "Вставити рядок вище", "", False), ("add", "Вставити рядок нижче", "", False),
             ("add", "Вставити стовпець зліва", "", False), ("add", "Вставити стовпець справа", "", False), "—",
             ("delete", "Видалити рядок", "", False), ("delete", "Видалити стовпець", "", False),
             ("delete", "Видалити таблицю", "", False), "—",
             ("table_rows", "Вирівняти висоту рядків", "", False),
             ("view_column", "Вирівняти ширину стовпців", "", False), "—",
             ("cell_merge", "Об’єднати клітинки", "", False), ("sort", "Сортувати таблицю", "", True), "—",
             ("table", "Параметри таблиці", "", False)]
FORMAT = [("format_bold", "Текст", "", True), ("format_size", "Стилі абзаців", "", True),
          ("format_align_left", "Вирівняти й додати відступ", "", True),
          ("format_line_spacing", "Інтервали між абзацами або рядками", "", True),
          ("view_column", "Колонки", "", True), ("format_list_bulleted", "Маркери й нумерація", "", True), "—",
          ("view_agenda", "Колонтитули", "", False), ("tag", "Номери сторінок", "", False),
          ("crop_rotate", "Орієнтація сторінки", "", False), "—",
          ("table", "Таблиця", "", True), ("image", "Зображення", "", True), ("border_style", "Межі й лінії", "", True),
          "—", ("format_clear", "Очистити форматування", "Ctrl+\\", False)]

# Обтікання: панель під виділеним зображенням (зліва направо).
WRAP = [("inline", "Відповідно до тексту"), ("wrap", "Обтікання текстом"), ("break", "Розрив тексту"),
        ("behind", "За текстом"), ("front", "Перед текстом")]

ALIGN = [("format_align_left", "Вирівняти за лівим краєм", "Ctrl+Shift+L"),
         ("format_align_center", "Вирівняти за центром", "Ctrl+Shift+E"),
         ("format_align_right", "Вирівняти за правим краєм", "Ctrl+Shift+R"),
         ("format_align_justify", "Вирівняти за шириною", "Ctrl+Shift+J")]

from dokument import ART  # ті самі умовні «фото», що й на слайдах (хом’як, пейзаж, ліс)



TRI = ('<svg width="20" height="20" viewBox="0 0 20 20" style="flex:none"><path d="M8 5.5 L13.5 10 L8 14.5Z" '
       'fill="#444746"/></svg>')


def esc(s):
    import html
    return html.escape(str(s), quote=True)


def _fonts():
    """Шрифти: Google Sans, Roboto й Material Symbols — з npm (лежать у кеші, у сховище не потрапляють)."""
    need = [os.path.join(FONTS, "node_modules", "material-symbols", "material-symbols-outlined.woff2"),
            os.path.join(FONTS, "node_modules", "@fontsource", "google-sans", "files",
                         "google-sans-cyrillic-400-normal.woff2")]
    if not all(os.path.exists(p) for p in need):
        os.makedirs(FONTS, exist_ok=True)
        subprocess.run(["npm", "i", "--silent", "--prefix", FONTS, "material-symbols", "@fontsource/google-sans",
                        "@fontsource/roboto"], check=True, capture_output=True)
    nm = os.path.join(FONTS, "node_modules")
    faces = [("Material Symbols Outlined", "material-symbols/material-symbols-outlined.woff2", 400, "")]
    for fam, pkg in [("Google Sans", "google-sans"), ("Roboto", "roboto")]:
        for sub in ["latin", "cyrillic", "latin-ext", "cyrillic-ext"]:
            for wgt in [400, 500, 700]:
                f = f"@fontsource/{pkg}/files/{pkg}-{sub}-{wgt}-normal.woff2"
                if os.path.exists(os.path.join(nm, f)):
                    faces.append((fam, f, wgt, ""))
    css = ""
    for fam, f, wgt, _ in faces:
        css += (f"@font-face{{font-family:'{fam}';font-weight:{wgt};font-style:normal;"
                f"src:url('file://{os.path.join(nm, f)}') format('woff2')}}\n")
    return css


def ic(name, size=20, color=None, fill=0, weight=400, cls=""):
    st = f"font-size:{size}px;font-variation-settings:'FILL' {fill},'wght' {weight},'GRAD' 0,'opsz' {min(48, max(20, size))}"
    if color:
        st += f";color:{color}"
    return f'<span class="ms {cls}" style="{st}">{name}</span>'


def wrap_icon(kind, size=24, color="#444746"):
    """Значки обтікання, як на панелі під зображенням у Google Документах."""
    ln = lambda x, y, w: f'<rect x="{x}" y="{y}" width="{w}" height="2" rx="1" fill="{color}"/>'
    img = lambda x, y, w, h, op=1: (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="1.5" fill="none" '
                                    f'stroke="{color}" stroke-width="1.8" opacity="{op}"/>'
                                    f'<path d="M{x + 2} {y + h - 2} l{w * .3} {-h * .4} l{w * .25} {h * .25} '
                                    f'l{w * .2} {-h * .15} l{w * .2} {h * .3}" fill="none" stroke="{color}" '
                                    f'stroke-width="1.4" opacity="{op}"/>')
    if kind == "inline":
        body = ln(3, 5, 18) + img(3, 9, 9, 8) + ln(14, 15, 7) + ln(3, 19, 18)
    elif kind == "wrap":
        body = ln(3, 4, 18) + img(3, 8, 9, 9) + ln(14, 9, 7) + ln(14, 14, 7) + ln(3, 20, 18)
    elif kind == "break":
        body = ln(3, 4, 18) + img(7, 8, 10, 9) + ln(3, 20, 18)
    elif kind == "behind":
        body = (f'<rect x="6" y="5" width="12" height="14" rx="1.5" fill="{color}" opacity=".25"/>'
                + ln(3, 7, 18) + ln(3, 11, 18) + ln(3, 15, 18) + ln(3, 19, 18))
    else:  # front
        body = (ln(3, 7, 18) + ln(3, 11, 18) + ln(3, 15, 18) + ln(3, 19, 18)
                + f'<rect x="6" y="5" width="12" height="14" rx="1.5" fill="#fff" stroke="{color}" stroke-width="1.8"/>')
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24">{body}</svg>'


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%(W)dpx;height:%(H)dpx;overflow:hidden;background:#F9FBFD;font-family:'Google Sans',Roboto,Arial,sans-serif;
  color:#1F1F1F;-webkit-font-smoothing:antialiased}
.ms{font-family:'Material Symbols Outlined';font-weight:normal;font-style:normal;line-height:1;display:inline-block;
  white-space:nowrap;direction:ltr;-webkit-font-feature-settings:'liga';color:#444746;user-select:none}
#hdr{position:absolute;left:0;top:0;right:0;height:64px}
#logo{position:absolute;left:16px;top:12px}
#title{position:absolute;left:68px;top:9px;font-size:18px;line-height:24px;display:flex;align-items:center;gap:6px}
#title .t{padding:0 3px}
#menus{position:absolute;left:62px;top:36px;display:flex;font-size:14px;line-height:24px}
#menus div{padding:0 7px;border-radius:4px;height:24px}
#menus div.on{background:#E1E5EA}
#right{position:absolute;right:16px;top:12px;display:flex;align-items:center;gap:6px}
.rb{width:40px;height:40px;border-radius:20px;display:flex;align-items:center;justify-content:center}
#tb{position:absolute;left:16px;right:16px;top:70px;height:40px;background:#EDF2FA;border-radius:24px;display:flex;
  align-items:center;padding:0 10px;font-size:14px}
.b{height:28px;min-width:28px;border-radius:4px;display:flex;align-items:center;justify-content:center;margin:0 1px;
  padding:0 2px;position:relative}
.b.on{background:#D3E3FD}.b.on .ms{color:#041E49}
.b .dd-ar{margin-left:-4px}
.sep{display:block;width:1px;height:20px;background:#C7C7C7;margin:0 6px}
.drop{height:28px;display:flex;align-items:center;padding:0 4px 0 8px;border-radius:4px;gap:2px;color:#444746}
.size{display:flex;align-items:center;gap:2px}
.size .v{width:38px;height:28px;border:1px solid #747775;border-radius:4px;display:flex;align-items:center;
  justify-content:center;font-size:14px;color:#1F1F1F}
#ruler{position:absolute;top:118px;height:24px}
#canvas{position:absolute;left:0;right:0;top:146px;bottom:0;overflow:hidden}
.page{position:absolute;background:#fff;border:1px solid #DADCE0;box-shadow:0 1px 3px rgba(60,64,67,.15);
  font-family:Arial,sans-serif;font-size:14.67px;line-height:1.38;color:#000}
.page p{margin:0 0 0 0;min-height:20px;white-space:pre-wrap}
.page h1{font-size:26px;font-weight:400;margin:0 0 8px 0;font-family:Arial}
.page ul,.page ol{margin:0;padding-left:46px}
.page li{padding-left:4px}
.page table{border-collapse:collapse;margin:6px 0}
.page td{border:1px solid #000;padding:5px 7px;vertical-align:top;font-size:14.67px}
.caret{display:inline-block;width:2px;height:18px;background:#000;vertical-align:-3px;margin:0 -1px}
.sel{background:#C3DAFB}
.dd{position:absolute;background:#fff;border-radius:6px;box-shadow:0 2px 6px 2px rgba(60,64,67,.15),0 1px 2px rgba(60,64,67,.3);
  padding:6px 0;font-size:14px;z-index:20;min-width:200px}
.it{height:36px;display:flex;align-items:center;padding:0 12px 0 16px;gap:14px;white-space:nowrap;color:#1F1F1F}
.it .ms{width:20px;text-align:center;color:#444746}
.it .lbl{flex:1}
.it .kb{color:#5F6368;font-size:13px;margin-left:24px}
.it.hl{background:#E8EAED}
.badge{background:#0B57D0;color:#fff;font-size:12px;font-weight:500;padding:2px 8px;border-radius:10px;margin-left:16px}
.hr{height:1px;background:#E3E3E3;margin:6px 0}
.tip{position:absolute;background:#3C4043;color:#fff;font-size:12px;line-height:16px;padding:5px 8px;border-radius:4px;
  white-space:nowrap;z-index:40;font-family:Roboto,Arial,sans-serif}
.wrapbar{position:absolute;display:flex;align-items:center;background:#fff;border-radius:6px;padding:2px 4px;gap:2px;
  box-shadow:0 1px 3px rgba(60,64,67,.3),0 4px 8px 3px rgba(60,64,67,.15);z-index:15}
.wrapbar .w{width:32px;height:32px;border-radius:4px;display:flex;align-items:center;justify-content:center}
.wrapbar .w.on{background:#D3E3FD}
.imgsel{display:block;position:absolute;inset:0;border:1px solid #1A73E8;pointer-events:none}
.h{display:block;position:absolute;width:9px;height:9px;background:#fff;border:1px solid #1A73E8}
.mark{position:absolute;border:3.5px solid %(MARK)s;border-radius:8px;z-index:50;pointer-events:none}
.num{position:absolute;width:30px;height:30px;border-radius:15px;background:%(MARK)s;color:#fff;font:700 18px/30px Roboto,Arial;
  text-align:center;z-index:51;box-shadow:0 0 0 2.5px #fff}
.cur{position:absolute;z-index:60;width:22px;height:30px}
.grid{padding:8px 14px 10px}
.grid .g{display:grid;gap:4px}
.grid .c{width:20px;height:20px;border:1px solid #C4C7C5;border-radius:2px;background:#fff}
.grid .c.on{background:#D3E3FD;border-color:#0B57D0}
.grid .gl{text-align:center;font-size:14px;margin-top:8px;color:#1F1F1F}
.dialog{position:absolute;background:#fff;border-radius:8px;box-shadow:0 4px 8px 3px rgba(60,64,67,.15),0 1px 3px rgba(60,64,67,.3);
  z-index:30;font-size:14px;padding:24px}
.scrim{position:absolute;inset:0;background:rgba(0,0,0,.45);z-index:25}
"""

JS = """
document.fonts.ready.then(function(){ setTimeout(function(){
  const R = e => e.getBoundingClientRect();
  // меню під пунктом верхнього меню / кнопкою; підменю — праворуч від пункту
  document.querySelectorAll('[data-anchor]').forEach(dd => {
    const a = document.querySelector(dd.dataset.anchor); if (!a) return;
    const r = R(a);
    if (dd.dataset.place === 'right') { dd.style.left = (r.right - 2) + 'px'; dd.style.top = (r.top - 6) + 'px'; }
    else if (dd.dataset.place === 'below-center') { const w = R(dd).width; dd.style.left = (r.left + r.width/2 - w/2) + 'px'; dd.style.top = (r.bottom + 6) + 'px'; }
    else if (dd.dataset.place === 'at-right') { dd.style.left = (r.right - 10) + 'px'; dd.style.top = (r.top + r.height*0.6) + 'px'; }
    else if (dd.dataset.place === 'at') { dd.style.left = (r.left + r.width*0.55) + 'px'; dd.style.top = (r.top + r.height*0.6) + 'px'; }
    else { dd.style.left = r.left + 'px'; dd.style.top = (r.bottom + 2) + 'px'; }
  });
  // виправляємо, щоб меню не вилазило за край
  document.querySelectorAll('.dd,.tip').forEach(dd => {
    const r = R(dd), W = innerWidth, H = innerHeight;
    if (r.right > W - 4) dd.style.left = (W - 4 - r.width) + 'px';
    if (r.bottom > H - 4) dd.style.top = Math.max(4, H - 4 - r.height) + 'px';
  });
  document.querySelectorAll('[data-anchor]').forEach(dd => {
    if (dd.dataset.place !== 'right') return;
    const a = document.querySelector(dd.dataset.anchor), r = R(a), d = R(dd);
    if (d.left < r.right - 10) dd.style.left = (r.left - d.width + 2) + 'px';
  });
  // підказки
  document.querySelectorAll('.tip[data-for]').forEach(t => {
    const a = document.querySelector(t.dataset.for); if (!a) return;
    const r = R(a), w = R(t).width;
    t.style.left = Math.max(4, r.left + r.width/2 - w/2) + 'px'; t.style.top = (r.bottom + 6) + 'px';
  });
  // позначки кроків
  (window.MARKS || []).forEach(m => {
    const els = [...document.querySelectorAll(m.sel)]; if (!els.length) { document.title = 'NOMARK ' + m.sel; return; }
    let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
    els.forEach(e => { const r = R(e); x0=Math.min(x0,r.left); y0=Math.min(y0,r.top); x1=Math.max(x1,r.right); y1=Math.max(y1,r.bottom); });
    const p = m.pad;
    if (m.ring) { const d = document.createElement('div'); d.className='mark';
      Object.assign(d.style,{left:(x0-p)+'px',top:(y0-p)+'px',width:(x1-x0+2*p)+'px',height:(y1-y0+2*p)+'px'}); document.body.appendChild(d); }
    if (m.n !== null) { const n = document.createElement('div'); n.className='num'; n.textContent = m.n;
      let nx, ny; const s = m.side;
      if (s==='left') { nx = x0-p-36; ny = (y0+y1)/2-15; } else if (s==='right') { nx = x1+p+6; ny=(y0+y1)/2-15; }
      else if (s==='top') { nx = (x0+x1)/2-15; ny = y0-p-36; } else if (s==='bottom') { nx=(x0+x1)/2-15; ny=y1+p+6; }
      else { nx = x0-p-16; ny = y0-p-16; }
      n.style.left = nx+'px'; n.style.top = ny+'px'; document.body.appendChild(n); }
    if (m.cursor) { const c = document.createElement('div'); c.className='cur';
      c.innerHTML = '<svg width="22" height="30" viewBox="0 0 22 30"><path d="M2 2 L2 24 L8 18.5 L12 27 L15.5 25.5 L11.5 17 L19 17 Z" fill="#000" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>';
      c.style.left = ((x0+x1)/2 - 2) + 'px'; c.style.top = ((y0+y1)/2 - 2) + 'px'; document.body.appendChild(c); }
  });
  window.DONE = 1;
}, 50); });
"""


class Doc:
    """Одне вікно Google Документів. Додаємо вміст сторінки, відкриті меню, підказки й позначки — і shot()."""

    def __init__(self, title="Документ без назви", width=1440, height=860, page_w=794, zoom="100%",
                 style="Звичайний текст", font="Arial", size=11, page_x=None):
        self.page_x = page_x  # зсунути сторінку, щоб текст стояв під потрібною кнопкою (вужчий кроп)
        self.title, self.W, self.H, self.page_w = title, width, height, page_w
        self.zoom, self.style, self.font, self.size = zoom, style, font, size
        self.body = ""
        self.over = []
        self.marks = []
        self.on = set()       # натиснуті кнопки панелі: 'bold', 'bullet', 'align-center', ...
        self.top_on = None    # відкрите верхнє меню
        self.page_top = 20
        self.table_tools = False  # виділено клітинки таблиці: на панелі з’являються заливка й межі

    # ---------- вміст сторінки ----------
    @staticmethod
    def p(text="", align="left", bold=False, size=None, caret=False, sel=False, style=""):
        t = f'<span class="sel">{text}</span>' if sel else text
        if bold:
            t = f"<b>{t}</b>"
        if caret:
            t += '<span class="caret"></span>'
        fs = f"font-size:{size * 1.333:.2f}px;" if size else ""
        return f'<p style="text-align:{align};{fs}{style}">{t}</p>'

    @staticmethod
    def ul(items, ordered=False, sel=False):
        tag = "ol" if ordered else "ul"
        inner = "".join(f'<li>{f"<span class=sel>{i}</span>" if sel else i}</li>' for i in items)
        return f"<{tag}>{inner}</{tag}>"

    @staticmethod
    def table(rows, widths=None, head_bold=False, fills=None, sel=None, caret=None, aligns=None, tid="t1"):
        """sel — набір (r, c) виділених клітинок; caret — (r, c), де стоїть курсор."""
        fills = fills or {}
        sel = sel or set()
        out = f'<table id="{tid}">'
        for r, row in enumerate(rows):
            out += f'<tr data-row="{r}">'
            for c_, v in enumerate(row):
                st = ""
                if widths:
                    st += f"width:{widths[c_]}px;"
                bg = fills.get((r, c_), fills.get((r, None)))
                if (r, c_) in sel:
                    bg = "#C3DAFB"
                if bg:
                    st += f"background:{bg};"
                if aligns:
                    st += f"text-align:{aligns[c_]};"
                txt = f"<b>{v}</b>" if head_bold and r == 0 else v
                if caret == (r, c_):
                    txt += '<span class="caret"></span>'
                out += f'<td data-cell="{r}-{c_}" style="{st}">{txt}</td>'
            out += "</tr>"
        return out + "</table>"

    @staticmethod
    def image(art="landscape", w=240, h=180, selected=False, mode="inline", float_side="left", iid="img1",
              wrapbar=False, wrap_on="inline", margin=12):
        """Зображення в тексті. mode: inline (у рядку), wrap (обтікання), break (окремо по центру)."""
        if mode == "wrap":
            st = f"float:{float_side};margin:4px {margin if float_side == 'left' else 0}px 6px {margin if float_side == 'right' else 0}px;"
        elif mode == "break":
            st = "display:block;margin:6px auto;"
        else:
            st = "display:inline-block;vertical-align:bottom;"
        hs = ""
        if selected:
            pts = [(0, 0), (.5, 0), (1, 0), (0, .5), (1, .5), (0, 1), (.5, 1), (1, 1)]
            hs = '<span class="imgsel"></span>' + "".join(
                f'<span class="h" data-h="{"corner" if px in (0, 1) and py in (0, 1) else "side"}-{k}" '
                f'style="left:{px * w - 4.5}px;top:{py * h - 4.5}px"></span>' for k, (px, py) in enumerate(pts))
            hs += (f'<span class="h" data-h="rot" style="left:{w / 2 - 4.5}px;top:-26px;border-radius:50%"></span>'
                   f'<span style="position:absolute;left:{w / 2}px;top:-17px;width:1px;height:17px;background:#1A73E8"></span>')
        bar = ""
        if selected and wrapbar:
            bar = (f'<span class="wrapbar" id="wrapbar" style="left:0px;top:{h + 8}px">'
                   + "".join(f'<span class="w{" on" if k == wrap_on else ""}" data-wrap="{k}">{wrap_icon(k)}</span>'
                             for k, _ in WRAP)
                   + '<span class="sep" style="margin:0 3px"></span>'
                   + f'<span class="w" data-wrap="edit">{ic("edit", 20)}</span>'
                   + f'<span class="w" data-wrap="more">{ic("more_vert", 20)}</span></span>')
        return (f'<span id="{iid}" style="position:relative;width:{w}px;height:{h}px;{st}">'
                f'<svg width="{w}" height="{h}" viewBox="0 0 160 120" preserveAspectRatio="xMidYMid slice" '
                f'style="display:block">{ART[art]}</svg>{hs}{bar}</span>')

    def page(self, html, top=20):
        self.body = html
        self.page_top = top

    # ---------- меню й накладки ----------
    @staticmethod
    def _items(items, hl=None, sub_id=None):
        hl = hl if isinstance(hl, (list, tuple, set)) else ([hl] if hl else [])
        out = ""
        for it in items:
            if it == "—":
                out += '<div class="hr"></div>'
                continue
            icon, label, kb, sub = it[:4]
            badge = it[4] if len(it) > 4 else ""
            cls = "it hl" if label in hl else "it"
            if icon == "function":
                iconh = '<span style="width:20px;font:16px/1 Times New Roman,serif;color:#444746">π<sup style="font-size:9px">2</sup></span>'
            else:
                iconh = ic(icon, 20) if icon else ""
            out += (f'<div class="{cls}" data-item="{esc(label)}">{iconh}'
                    f'<span class="lbl">{label}</span>'
                    f'{f"<span class=badge>{badge}</span>" if badge else ""}'
                    f'{f"<span class=kb>{kb}</span>" if kb else ""}'
                    f'{TRI if sub else ""}</div>')
        return out

    def menu_bar_open(self, name, items, hl=None, sub=None, sub_items=None, sub_hl=None, sub_html=None, cut=None):
        """Відкрите верхнє меню. sub — пункт, з якого відкрито підменю (sub_items або довільний sub_html).
        cut — показати лише перші N пунктів (решту однаково обріжемо кропом)."""
        self.top_on = name
        its = items if cut is None else items[:cut]
        self.over.append(f'<div class="dd" id="dd-main" data-anchor="[data-top=\'{name}\']">{self._items(its, hl or sub)}</div>')
        if sub:
            inner = sub_html if sub_html is not None else self._items(sub_items, sub_hl)
            self.over.append(f'<div class="dd" id="dd-sub" data-anchor="#dd-main [data-item=\'{sub}\']" '
                             f'data-place="right">{inner}</div>')

    def button_menu(self, button, html, min_w=None, place=""):
        """Випадне меню під кнопкою панелі (вирівнювання, списки, міжрядковий інтервал)."""
        self.on.add(button)
        mw = f"min-width:{min_w}px;" if min_w else ""
        self.over.append(f'<div class="dd" id="dd-btn" style="{mw}" data-anchor="[data-b=\'{button}\']" '
                         f'data-place="{place}">{html}</div>')

    def context_menu(self, at_sel, items, hl=None, place="at"):
        self.over.append(f'<div class="dd" id="dd-ctx" data-anchor="{at_sel}" data-place="{place}">{self._items(items, hl)}</div>')

    def tooltip(self, sel, text):
        self.over.append(f'<div class="tip" data-for="{esc(sel)}">{text}</div>')

    @staticmethod
    def table_grid(cols, rows):
        """Сітка, як у справжніх Документах (скрін учителя: на 5 x 3 видно 11 стовпців і 5 рядків)."""
        nc, nr = max(11, cols + 6), max(5, rows + 2)
        cells = "".join(f'<div class="c{" on" if r < rows and c_ < cols else ""}"></div>'
                        for r in range(nr) for c_ in range(nc))
        return (Doc._items([("note_add", "Шаблони", "", True)]) + '<div class="hr"></div>'
                f'<div class="grid"><div class="g" id="tgrid" style="grid-template-columns:repeat({nc},20px)">{cells}</div>'
                f'<div class="gl" id="tgl">{cols} x {rows}</div></div>')

    @staticmethod
    def align_menu(on="format_align_left"):
        cells = "".join(f'<div class="b{" on" if k == on else ""}" data-al="{k}" style="width:32px;height:32px">{ic(k, 20)}</div>'
                        for k, _, _ in ALIGN)
        return f'<div style="display:flex;gap:4px;padding:2px 8px">{cells}</div>'

    @staticmethod
    def spacing_menu(on="1,15"):
        out = ""
        for v in ["Одинарний", "1,15", "1,5", "Подвійний"]:
            mark = ic("check", 20) if v == on else '<span style="width:20px;display:inline-block"></span>'
            out += f'<div class="it" data-item="{v}">{mark}<span class="lbl">{v}</span></div>'
        return out

    def page_setup(self, orient="portrait", hl=None):
        """Вікно «Налаштування сторінки» (Файл → Налаштування сторінки)."""
        radio = lambda on: (f'<span style="display:inline-block;width:20px;height:20px;border-radius:50%;border:2px solid '
                            f'{"#0B57D0" if on else "#444746"};position:relative;vertical-align:-5px;margin-right:8px">'
                            + ('<span style="position:absolute;left:3px;top:3px;width:10px;height:10px;border-radius:50%;'
                               'background:#0B57D0"></span>' if on else "") + "</span>")
        field = lambda lab, v: (f'<div style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin:6px 0">'
                                f'<span>{lab}</span><span style="width:84px;height:32px;border:1px solid #747775;'
                                f'border-radius:4px;display:inline-flex;align-items:center;padding:0 10px">{v}</span></div>')
        tabs = ('<div style="display:flex;border-bottom:1px solid #E3E3E3;margin:0 -24px 16px;padding:0 24px">'
                '<div style="padding:10px 18px;color:#0B57D0;border-bottom:3px solid #0B57D0;font-weight:500">Сторінки</div>'
                '<div style="padding:10px 18px;color:#444746">Без поділу на сторінки</div></div>')
        html = (f'<div class="scrim"></div><div class="dialog" id="psetup" style="left:{self.W / 2 - 280}px;top:150px;width:560px">'
                '<div style="font-size:22px;margin-bottom:14px">Налаштування сторінки</div>' + tabs +
                '<div style="display:flex;gap:40px"><div style="flex:1">'
                '<div style="font-weight:500;margin-bottom:8px">Орієнтація</div>'
                f'<div id="or-portrait" style="margin:6px 0">{radio(orient == "portrait")}Книжкова</div>'
                f'<div id="or-landscape" style="margin:6px 0 18px">{radio(orient == "landscape")}Альбомна</div>'
                '<div style="font-weight:500;margin-bottom:8px">Розмір паперу</div>'
                '<div style="width:220px;height:36px;border:1px solid #747775;border-radius:4px;display:flex;align-items:center;'
                'justify-content:space-between;padding:0 10px;margin-bottom:18px">A4 (21 см x 29,7 см)'
                + ic("arrow_drop_down", 22) + '</div>'
                '<div style="font-weight:500;margin-bottom:8px">Колір сторінки</div>'
                '<div style="width:44px;height:28px;border:1px solid #747775;border-radius:4px;background:#fff"></div></div>'
                '<div id="ps-margins" style="width:200px"><div style="font-weight:500;margin-bottom:8px">Поля '
                '<span style="color:#5F6368;font-weight:400">(сантиметри)</span></div>'
                + field("Угорі", "2,54") + field("Унизу", "2,54") + field("Ліворуч", "2,54") + field("Праворуч", "2,54")
                + '</div></div><div style="display:flex;justify-content:flex-end;gap:8px;margin-top:22px;align-items:center">'
                '<div style="color:#0B57D0;padding:8px 14px;margin-right:auto">Використовувати за умовчанням</div>'
                '<div style="color:#0B57D0;padding:8px 14px;border:1px solid #747775;border-radius:18px">Скасувати</div>'
                '<div id="ps-ok" style="color:#fff;background:#0B57D0;padding:8px 22px;border-radius:18px">OK</div></div></div>')
        self.over.append(html)

    def mark(self, sel, n=None, pad=4, side="tl", ring=True, cursor=False):
        """Помаранчева рамка навколо елемента (або групи) і кружечок із номером кроку."""
        self.marks.append({"sel": sel, "n": n, "pad": pad, "side": side, "ring": ring, "cursor": cursor})

    # ---------- вікно ----------
    def _toolbar(self):
        def b(key, icon, sub=False, fill=0):
            cls = "b on" if key in self.on else "b"
            return (f'<div class="{cls}" data-b="{key}">{ic(icon, 20, fill=fill)}'
                    f'{ic("arrow_drop_down", 18, cls="dd-ar") if sub else ""}</div>')
        drop = lambda key, text, w: (f'<div class="drop{" b on" if key in self.on else ""}" data-b="{key}" '
                                     f'style="width:{w}px;justify-content:space-between">'
                                     f'<span style="overflow:hidden;white-space:nowrap;text-overflow:ellipsis">{text}</span>{ic("arrow_drop_down", 18)}</div>')
        sep = '<div class="sep"></div>'
        color_a = ('<div class="b" data-b="color" style="flex-direction:column;gap:0">'
                   f'{ic("format_color_text", 20)}</div>')
        return (b("search", "search") + b("undo", "undo") + b("redo", "redo") + b("print", "print")
                + b("spell", "spellcheck") + b("paint", "format_paint") + drop("zoom", self.zoom, 64) + sep
                + drop("style", self.style, 132) + sep + drop("font", self.font, 96) + sep
                + f'<div class="size" data-b="size">{b("minus", "remove")}<div class="v">{self.size}</div>{b("plus", "add")}</div>'
                + sep + b("bold", "format_bold") + b("italic", "format_italic") + b("underline", "format_underlined")
                + color_a + b("highlight", "ink_highlighter")
                + ((b("fill", "format_color_fill") + b("bcolor", "border_color") + b("bwidth", "line_weight")
                    + b("bdash", "line_style")) if self.table_tools else "") + sep
                + b("link", "link") + b("comment", "add_comment") + b("image", "image") + sep
                + b("align", self.align_icon, True)
                + b("spacing", "format_line_spacing") + b("check", "checklist", True)
                + b("bullet", "format_list_bulleted", True) + b("number", "format_list_numbered", True)
                + b("indl", "format_indent_decrease") + b("indr", "format_indent_increase") + b("clear", "format_clear")
                + '<div style="flex:1"></div>' + b("mode", "edit", True) + sep + b("collapse", "keyboard_arrow_up"))

    align_icon = "format_align_left"

    def _ruler(self, left):
        ppcm = 37.8
        out = (f'<div id="ruler" style="left:{left}px;width:{self.page_w}px">'
               f'<div style="position:absolute;left:0;width:{2.54 * ppcm}px;top:4px;height:16px;background:#E8EAED"></div>'
               f'<div style="position:absolute;right:0;width:{2.54 * ppcm}px;top:4px;height:16px;background:#E8EAED"></div>')
        x0 = 2.54 * ppcm
        k = -2
        while x0 + k * ppcm <= self.page_w + 1:
            x = x0 + k * ppcm
            if k != 0 and x >= 0:
                out += (f'<div style="position:absolute;left:{x - 10}px;top:4px;width:20px;text-align:center;'
                        f'font:10px Roboto;color:#444746">{abs(k)}</div>')
            for q in (0.25, 0.5, 0.75):
                xx = x + q * ppcm
                if 0 <= xx <= self.page_w:
                    out += (f'<div style="position:absolute;left:{xx}px;top:{9 if q == .5 else 12}px;width:1px;'
                            f'height:{7 if q == .5 else 4}px;background:#80868B"></div>')
            k += 1
        tri = lambda x, t: (f'<svg style="position:absolute;left:{x - 6}px;top:{t}px" width="12" height="10">'
                            f'<path d="M0 0 H12 L6 8Z" fill="#4285F4"/></svg>')
        out += tri(x0, 2) + f'<div style="position:absolute;left:{x0 - 6}px;top:0;width:12px;height:3px;background:#4285F4"></div>'
        out += tri(self.page_w - x0, 2)
        return out + "</div>"

    def html(self):
        left = self.page_x if self.page_x is not None else max(24, (self.W - self.page_w) / 2)
        logo = ('<svg id="logo" width="28" height="40" viewBox="0 0 28 40"><path d="M3 0h15l10 10v27a3 3 0 0 1-3 3H3a3 3 0 0 1-3-3V3a3 3 0 0 1 3-3z" fill="#4285F4"/>'
                '<path d="M18 0l10 10h-7a3 3 0 0 1-3-3z" fill="#A1C2FA"/><rect x="7" y="19" width="14" height="2.4" rx="1" fill="#fff"/>'
                '<rect x="7" y="24" width="14" height="2.4" rx="1" fill="#fff"/><rect x="7" y="29" width="10" height="2.4" rx="1" fill="#fff"/></svg>')
        menus = "".join(f'<div data-top="{m}" class="{"on" if m == self.top_on else ""}">{m}</div>' for m in TOP)
        gem = ('<svg width="22" height="22" viewBox="0 0 24 24"><defs><linearGradient id="gg" x1="0" y1="0" x2="1" y2="1">'
               '<stop offset="0" stop-color="#4285F4"/><stop offset=".5" stop-color="#9B72CB"/><stop offset="1" stop-color="#D96570"/></linearGradient></defs>'
               '<path d="M12 1c.6 5.6 4.4 10.4 11 11-6.6.6-10.4 5.4-11 11-.6-5.6-4.4-10.4-11-11 6.6-.6 10.4-5.4 11-11z" fill="url(#gg)"/></svg>')
        right = (f'<div class="rb">{ic("comment", 24)}</div><div class="rb" style="width:56px">{ic("videocam", 24)}{ic("arrow_drop_down", 20)}</div>'
                 f'<div class="rb" style="background:#C2E7FF">{ic("person_add", 22, "#001D35")}</div>'
                 f'<div class="rb">{gem}</div><div class="rb"><div style="width:32px;height:32px;border-radius:16px;'
                 f'background:#7CACF8;color:#fff;font:500 16px/32px Roboto;text-align:center">У</div></div>')
        page = (f'<div class="page" id="page" style="left:{left}px;top:{self.page_top}px;width:{self.page_w}px;'
                f'min-height:{max(400, self.H)}px;padding:56px 96px">{self.body}</div>')
        tabsbtn = (f'<div style="position:absolute;left:24px;top:18px;width:40px;height:40px;border-radius:20px;'
                   f'display:flex;align-items:center;justify-content:center">{ic("format_list_bulleted", 22)}</div>')
        return ("<!doctype html><html><head><meta charset='utf-8'><style>" + _fonts()
                + CSS % {"W": self.W, "H": self.H, "MARK": MARK} + "</style></head><body>"
                + f'<div id="hdr">{logo}<div id="title"><span class="t">{esc(self.title)}</span>{ic("star", 20)}'
                + f'{ic("drive_file_move", 20)}{ic("cloud_done", 20)}</div><div id="menus">{menus}</div>'
                + f'<div id="right">{right}</div></div>'
                + f'<div id="tb">{self._toolbar()}</div>' + self._ruler(left)
                + f'<div id="canvas">{tabsbtn}{page}</div>' + "".join(self.over)
                + f"<script>window.MARKS={json.dumps(self.marks, ensure_ascii=False)};{JS}</script></body></html>")

    def shot(self, name, crop=None, pad=14, scale=2):
        """Рендерить у PNG справжнім Chrome. crop — CSS-селектори (рамка навколо всіх) або (x0, y0, x1, y1).
        Повертає шлях до PNG (кешується за вмістом)."""
        h = self.html()
        key = hashlib.md5((h + json.dumps(crop, ensure_ascii=False) + str(pad) + str(scale)
                           + open(__file__, encoding="utf-8").read()).encode()).hexdigest()[:12]
        os.makedirs(SHOT_CACHE, exist_ok=True)
        png = os.path.join(SHOT_CACHE, f"gdocs-{name}-{key}.png")
        if os.path.exists(png):
            return png
        src = os.path.join(SHOT_CACHE, f"gdocs-{name}-{key}.html")
        open(src, "w", encoding="utf-8").write(h)
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            br = p.chromium.launch(executable_path="/usr/bin/google-chrome")
            pg = br.new_page(viewport={"width": self.W, "height": self.H}, device_scale_factor=scale)
            pg.goto("file://" + src)
            pg.wait_for_function("window.DONE === 1", timeout=20000)
            pg.wait_for_timeout(100)
            t = pg.title()
            if t.startswith("NOMARK"):
                raise RuntimeError("Позначка не знайшла елемент: " + t)
            clip = None
            if crop:
                if isinstance(crop[0], (int, float)):
                    x0, y0, x1, y1 = crop
                else:
                    box = pg.evaluate("""sels => { let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
                      for (const s of sels) for (const e of document.querySelectorAll(s)) { const r=e.getBoundingClientRect();
                        x0=Math.min(x0,r.left); y0=Math.min(y0,r.top); x1=Math.max(x1,r.right); y1=Math.max(y1,r.bottom); }
                      for (const e of document.querySelectorAll('.num,.mark')) { const r=e.getBoundingClientRect();
                        x0=Math.min(x0,r.left); y0=Math.min(y0,r.top); x1=Math.max(x1,r.right); y1=Math.max(y1,r.bottom); }
                      return [x0,y0,x1,y1]; }""", list(crop))
                    x0, y0, x1, y1 = box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad
                x0, y0 = max(0, x0), max(0, y0)
                x1, y1 = min(self.W, x1), min(self.H, y1)
                clip = {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0}
            pg.screenshot(path=png, clip=clip)
            br.close()
        open(png + ".title", "w").write("Google Документи")
        return png


# ---------- на слайді ----------
from deck import Slide, data_uri, DARK_BG  # noqa: E402


def _gshot(self, x, y, w, png, maxh=None, align="left"):
    """Скрін Google Документів на слайді. Вписується в ширину w (і висоту maxh). Повертає (x, y, ширина, висота)."""
    from PIL import Image
    iw, ih = Image.open(png).size
    k = w / iw
    if maxh and ih * k > maxh:
        k = maxh / ih
    ww, hh = iw * k, ih * k
    css = k * 2  # PNG знято з масштабом 2
    if css < 1.45:
        print(f"  ! дрібний скрін {os.path.basename(png)}: шрифт інтерфейсу ≈ {14 * css:.0f} px на слайді")
    if align == "center":
        x = x + (w - ww) / 2
    elif align == "right":
        x = x + w - ww
    self.add(f'<img alt="" src="{data_uri(png)}" style="position:absolute;left:{x:.0f}px;top:{y}px;width:{ww:.0f}px;'
             f'height:{hh:.0f}px;border:2px solid {DARK_BG};border-radius:12px;box-sizing:content-box;'
             f'box-shadow:0 14px 40px rgba(30,40,60,0.22);background:#F9FBFD">')
    return x, y, ww, hh


def _gsteps(self, items, x=128, y=206, w=700, size=31, gap=20, start=1):
    """Кроки з помаранчевими номерами — такими самими, як позначки на скріні."""
    rows = []
    for i, it in enumerate(items, start):
        rows.append(
            f'<div style="display:flex;flex-direction:row;align-items:flex-start;gap:20px">'
            f'<div style="flex:none;width:48px;height:48px;border-radius:50%;background:{MARK};display:flex;'
            f'flex-direction:column;align-items:center;justify-content:center"><p style="font-size:26px;'
            f'font-weight:700;line-height:1.2;color:#FFFFFF">{i}</p></div>'
            f'<p style="flex:1;padding-top:3px;font-size:{size}px;font-weight:400;line-height:1.3;'
            f'color:{self.ink}">{it}</p></div>')
    self.add(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;display:flex;flex-direction:column;'
             f'gap:{gap}px">' + "".join(rows) + "</div>")


def _gsteps_row(self, items, x=128, y=220, w=1664, size=29, start=1):
    """Кроки в один рядок (над широким скріном панелі інструментів)."""
    cols = []
    for i, it in enumerate(items, start):
        cols.append(
            f'<div style="flex:1;display:flex;flex-direction:row;align-items:flex-start;gap:16px">'
            f'<div style="flex:none;width:46px;height:46px;border-radius:50%;background:{MARK};display:flex;'
            f'align-items:center;justify-content:center"><p style="font-size:25px;font-weight:700;color:#FFFFFF">{i}</p></div>'
            f'<p style="flex:1;padding-top:3px;font-size:{size}px;line-height:1.3;color:{self.ink}">{it}</p></div>')
    self.add(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;display:flex;flex-direction:row;'
             f'gap:28px">' + "".join(cols) + "</div>")


Slide.gsteps_row = _gsteps_row
Slide.gshot = _gshot
Slide.gsteps = _gsteps
