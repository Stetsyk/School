# -*- coding: utf-8 -*-
"""Роздруківки практичних завдань у зошиті.

Приклад:
    python3 "Tools/zoshyt/zoshyt.py" "5 клас 1-3 урок" "7 клас 10-12" "9 клас 1-3" "пайтон 1-5"

Класи 5-9 лежать у теці «Уроки/N клас», курс Python — у «Уроки/Пайтон».
Запит на Python: «пайтон 1-5», «python 13», «пайтон урок 7».

Збирає з файлів уроків тільки блок «🕯️ У зошиті» (між маркерами
<!-- ЗОШИТ:ПОЧАТОК --> і <!-- ЗОШИТ:КІНЕЦЬ -->), кладе кожен урок на
окрему сторінку A4 і робить один .docx та один .pdf.

Увесь текст друкується кеглем 14 pt без підбору розмаіру, тож запуск
швидкий: Chrome стартує один раз на весь документ. Інший кегль — ключ
--кегль. Якщо завдань багато, урок може зайняти дві сторінки — це нормально.

Потрібні лише pandoc і Google Chrome. Сторонніх бібліотек Python немає.
"""

import argparse
import io
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCHOOL = os.path.abspath(os.path.join(HERE, "..", ".."))
LESSONS_DIR = os.path.join(SCHOOL, "Уроки")
PY_LESSONS_DIR = os.path.join(LESSONS_DIR, "Пайтон")
OUT_DIR = os.path.join(SCHOOL, "Роздруківки")

OPEN_MARK = "<!-- ЗОШИТ:ПОЧАТОК -->"
CLOSE_MARK = "<!-- ЗОШИТ:КІНЕЦЬ -->"
ANSWERS_RE = re.compile(r"^#### ✅ Відповіді та орієнтири\s*$", re.M)

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
]


# усі уроки друкуються цим кеглем; перебору немає (можна змінити ключем --кегль)
DEFAULT_FONT_PT = 14.0

ROMAN = {"І": 1, "ІІ": 2, "I": 1, "II": 2}


# ---------------------------------------------------------------- пошук уроків

class Lesson(object):
    def __init__(self, path, grade, semester, numbers, title, course=None):
        self.path = path
        self.grade = grade
        self.semester = semester
        self.numbers = numbers
        self.title = title
        self.course = course          # None — класи 5-9; "python" — курс Python

    @property
    def label(self):
        nums = "-".join("%02d" % n for n in self.numbers)
        if self.course == "python":
            return "Урок %s" % nums
        rom = "І" if self.semester == 1 else "ІІ"
        return "Урок %s-%s" % (rom, nums)

    @property
    def heading(self):
        """Рядок над назвою уроку: «7 клас · Урок І-11» або «Python · Урок 13»."""
        if self.course == "python":
            return "Python · %s" % self.label
        return "%d клас · %s" % (self.grade, self.label)

    @property
    def sort_key(self):
        return (self.grade, self.semester, self.numbers[0])


FNAME_RE = re.compile(r"^Урок\s+(І{1,2}|I{1,2})-((?:\d{2})(?:-\d{2})*)\.\s*(.+)\.md$")

# Курс Python: «Урок 01. Назва.md» — без семестру й класу
PY_FNAME_RE = re.compile(r"^Урок\s+((?:\d{2})(?:-\d{2})*)\.\s*(.+)\.md$")


def scan_lessons():
    lessons = []
    if not os.path.isdir(LESSONS_DIR):
        die("не знайдено теку з уроками: %s" % LESSONS_DIR)
    for entry in sorted(os.listdir(LESSONS_DIR)):
        gdir = os.path.join(LESSONS_DIR, entry)
        if not os.path.isdir(gdir):
            continue
        gm = re.match(r"^(\d+)\s*клас$", entry)
        if not gm:
            continue          # «Позакласні заходи» тощо
        grade = int(gm.group(1))
        for name in sorted(os.listdir(gdir)):
            fm = FNAME_RE.match(name)
            if not fm:
                continue
            semester = ROMAN.get(fm.group(1), 1)
            numbers = [int(x) for x in fm.group(2).split("-")]
            lessons.append(Lesson(os.path.join(gdir, name), grade, semester,
                                  numbers, fm.group(3).strip()))
    return lessons


def scan_python_lessons():
    """Уроки курсу Python з теки «Уроки/Пайтон». Немає — просто порожній список."""
    lessons = []
    if not os.path.isdir(PY_LESSONS_DIR):
        return lessons
    for name in sorted(os.listdir(PY_LESSONS_DIR)):
        fm = PY_FNAME_RE.match(name)
        if not fm:
            continue
        numbers = [int(x) for x in fm.group(1).split("-")]
        lessons.append(Lesson(os.path.join(PY_LESSONS_DIR, name),
                              0, 0, numbers, fm.group(2).strip(),
                              course="python"))
    return lessons


SPEC_RE = re.compile(
    r"^\s*(\d+)\s*(?:клас\w*)?\s*"          # клас
    r"(?:(І{1,2}|I{1,2})\s*(?:семестр\w*)?\s*)?"   # семестр (необов'язково)
    r"(\d+)\s*(?:[-–—]\s*(\d+))?"           # номер або діапазон
    r"\s*(?:урок\w*)?\s*$", re.U)

# «пайтон 1-5», «python 13», «пайтон урок 7»
PY_SPEC_RE = re.compile(
    r"^\s*(?:python|пайтон\w*|пітон\w*)\s*(?:курс\w*)?\s*"
    r"(\d+)\s*(?:[-–—]\s*(\d+))?"
    r"\s*(?:урок\w*)?\s*$", re.U | re.I)


def parse_spec(text):
    """Повертає (course, grade, semester, lo, hi). course: None або "python"."""
    pm = PY_SPEC_RE.match(text)
    if pm:
        lo = int(pm.group(1))
        hi = int(pm.group(2)) if pm.group(2) else lo
        if hi < lo:
            lo, hi = hi, lo
        return "python", 0, 0, lo, hi
    m = SPEC_RE.match(text)
    if not m:
        die("не розумію запит «%s».\n"
            "   Формат: «5 клас 2-3 урок», «7 клас 11», «6 клас ІІ 4-6», "
            "«пайтон 1-5»." % text)
    grade = int(m.group(1))
    semester = ROMAN.get(m.group(2), 1) if m.group(2) else 1
    lo = int(m.group(3))
    hi = int(m.group(4)) if m.group(4) else lo
    if hi < lo:
        lo, hi = hi, lo
    return None, grade, semester, lo, hi


def select(lessons, specs):
    chosen, seen = [], set()
    for spec in specs:
        course, grade, semester, lo, hi = parse_spec(spec)
        if course == "python":
            hits = [ls for ls in lessons
                    if ls.course == "python"
                    and any(lo <= n <= hi for n in ls.numbers)]
        else:
            hits = [ls for ls in lessons
                    if ls.course is None and ls.grade == grade
                    and ls.semester == semester
                    and any(lo <= n <= hi for n in ls.numbers)]
        if not hits:
            warn("за запитом «%s» уроків не знайдено — пропускаю" % spec)
            continue
        # спарений урок затягує сусідній номер: чесно про це кажемо
        covered = sorted(set(n for ls in hits for n in ls.numbers))
        if covered[0] < lo or covered[-1] > hi:
            info("«%s» → уроки %d-%d (спарений урок не ріжеться навпіл)"
                 % (spec, covered[0], covered[-1]))
        for ls in hits:
            if ls.path not in seen:
                seen.add(ls.path)
                chosen.append(ls)
    chosen.sort(key=lambda ls: ls.sort_key)
    return chosen


# ------------------------------------------------------------------- витягання

def extract(lesson, with_answers=False):
    text = io.open(lesson.path, encoding="utf-8").read()
    blocks = re.findall(re.escape(OPEN_MARK) + r"(.*?)" + re.escape(CLOSE_MARK),
                        text, re.S)
    if not blocks:
        warn("%s: немає маркерів ЗОШИТ — урок пропущено" % lesson.label)
        return None
    body = "\n\n".join(b.strip() for b in blocks if b.strip())
    if with_answers:
        am = ANSWERS_RE.search(text)
        if am:
            tail = text[am.end():]
            end = re.search(r"^(---|## )", tail, re.M)
            answers = (tail[:end.start()] if end else tail).strip()
            if answers:
                body += "\n\n### ✅ Відповіді (для вчителя)\n\n" + answers
    return body


# --------------------------------------------------------------- markdown → html

TASK_RE = re.compile(
    r"^<strong>((?:Завдання|Частина|Задача|Задачі|Крок|Варіант|Бонус)[^<]*)</strong>")


def md_inline(s):
    s = (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    return s


def md_to_html(md):
    """Мінімальний markdown: заголовки, списки, таблиці, код, цитати."""
    out, lines, i = [], md.split("\n"), 0
    para = []

    def flush():
        if not para:
            return
        html = md_inline(" ".join(para).strip())
        m = TASK_RE.match(html)
        if m:
            # «**Завдання 3. Назва.**» виносимо окремим рядком з відступом,
            # умова йде наступним абзацом
            out.append('<p class="task"><strong>%s</strong></p>' % m.group(1))
            rest = html[m.end():].strip()
            if rest:
                out.append("<p>%s</p>" % rest)
        else:
            out.append("<p>%s</p>" % html)
        del para[:]

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            flush(); i += 1; continue

        if stripped.startswith("```"):
            flush()
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i]); i += 1
            i += 1
            esc = "\n".join(code).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            out.append("<pre>%s</pre>" % esc)
            continue

        hm = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if hm:
            flush()
            lvl = min(len(hm.group(1)) + 1, 6)
            out.append("<h%d>%s</h%d>" % (lvl, md_inline(hm.group(2)), lvl))
            i += 1; continue

        if stripped.startswith("|") and i + 1 < len(lines) \
                and re.match(r"^\s*\|[\s:\-|]+\|\s*$", lines[i + 1]):
            flush()
            head = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join("<th>%s</th>" % md_inline(c) for c in head)
            body = "".join("<tr>%s</tr>" % "".join(
                "<td>%s</td>" % md_inline(c) for c in r) for r in rows)
            out.append("<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>"
                       % (th, body))
            continue

        if stripped.startswith(">"):
            flush()
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i])); i += 1
            out.append("<blockquote>%s</blockquote>" % md_to_html("\n".join(quote)))
            continue

        lm = re.match(r"^(\s*)(\d+)\.\s+(.*)$", line)
        bm = re.match(r"^(\s*)[-*·]\s+(.*)$", line)
        if lm or bm:
            flush()
            ordered = bool(lm)
            items = []
            pat = r"^(\s*)(\d+)\.\s+(.*)$" if ordered else r"^(\s*)[-*·]\s+(.*)$"
            while i < len(lines):
                mm = re.match(pat, lines[i])
                if not mm:
                    if lines[i].strip() and lines[i].startswith(("    ", "\t")) and items:
                        items[-1] += " " + lines[i].strip(); i += 1; continue
                    break
                items.append(mm.group(3) if ordered else mm.group(2))
                i += 1
            tag = "ol" if ordered else "ul"
            out.append("<%s>%s</%s>" % (tag, "".join(
                "<li>%s</li>" % md_inline(x) for x in items), tag))
            continue

        para.append(stripped)
        i += 1

    flush()
    return "\n".join(out)


# ------------------------------------------------------------------------- HTML

CSS = u"""
@page { size: A4; margin: 12mm 12mm 12mm 12mm;
        @bottom-center {
          content: counter(page) " / " counter(pages);
          font-family: "PT Sans", "Helvetica Neue", Arial, sans-serif;
          font-size: 8.5pt; color: #555; } }
* { box-sizing: border-box; }
body { margin: 0; font-family: "PT Sans", "Helvetica Neue", Arial, sans-serif;
       color: #000; }
.page { page-break-after: always; }
.page:last-child { page-break-after: auto; }
.hdr { border-bottom: 1.6pt solid #000; padding-bottom: 2mm; margin-bottom: 3mm; }
.hdr .cls { font-weight: 700; letter-spacing: .04em; text-transform: uppercase; }
.hdr .ttl { font-weight: 700; margin-top: .6mm; }
.hdr .sub { margin-top: .8mm; }
.name { float: right; font-weight: 400; }
h2, h3, h4 { margin: 2.6mm 0 1.2mm; page-break-after: avoid; }
h2 { font-size: 1.12em; } h3 { font-size: 1.06em; } h4 { font-size: 1em; }
p { margin: 0 0 1.4mm; }
p.task { margin-top: 3.4mm; page-break-after: avoid; }
.page > p.task:first-of-type { margin-top: 0; }
ul, ol { margin: 0 0 1.6mm; padding-left: 5.5mm; }
li { margin-bottom: .5mm; }
table { border-collapse: collapse; width: 100%; margin: 1.4mm 0 2.2mm;
        page-break-inside: avoid; }
th, td { border: .6pt solid #444; padding: 1mm 1.4mm; text-align: left;
         vertical-align: top; }
th { background: #eee; font-weight: 700; }
pre { border: .6pt solid #888; background: #f6f6f6; padding: 1.2mm 1.8mm;
      margin: 1.2mm 0 1.8mm; white-space: pre-wrap;
      font-family: "SF Mono", Menlo, Consolas, monospace; font-size: .92em;
      page-break-inside: avoid; }
code { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: .94em; }
blockquote { margin: 1.2mm 0 1.8mm; padding-left: 2.4mm;
             border-left: 1.4pt solid #999; }
strong { font-weight: 700; }
"""


def page_html(lesson, body_html, font_pt, name_line):
    name = (u'<span class="name">Прізвище _______________  Дата ________</span>'
            if name_line else u"")
    return (u'<div class="page" style="font-size:%.1fpt; line-height:1.22">\n'
            u'  <div class="hdr">%s<div class="cls">%s</div>'
            u'<div class="ttl">%s</div>'
            u'<div class="sub">Практичні завдання в зошиті</div></div>\n'
            u'%s\n</div>' % (font_pt, name, esc(lesson.heading),
                             esc(lesson.title), body_html))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def document_html(pages_html, title):
    return (u'<!doctype html><html lang="uk"><head><meta charset="utf-8">'
            u'<title>%s</title><style>%s</style></head><body>\n%s\n'
            u'</body></html>' % (esc(title), CSS, "\n".join(pages_html)))


# -------------------------------------------------------------------- Chrome PDF
#
# На macOS 12 Chrome 150 у headless-режимі малює сторінку правильно, але сам
# не завершується і не віддає stdout. Тому PDF чекаємо як файл: щойно його
# розмір перестав змінюватись — вбиваємо процес самі.

def find_chrome():
    for p in CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    for name in ("google-chrome", "chromium", "chromium-browser"):
        p = shutil.which(name)
        if p:
            return p
    return None


def chrome_cmd(chrome, html_path, pdf_path, profile):
    return [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--no-pdf-header-footer", "--disable-extensions",
            "--disable-background-networking", "--no-first-run",
            "--user-data-dir=" + profile,
            "--print-to-pdf=" + pdf_path, "file://" + html_path]


def _kill(proc):
    try:
        proc.kill()
        proc.wait()
    except Exception:
        pass


def render_pdfs(chrome, jobs, tmpdir, timeout=90, parallel=4):
    """jobs: список (html_path, pdf_path). Рендерить пачками, повертає готові."""
    done = []
    for start in range(0, len(jobs), parallel):
        batch = jobs[start:start + parallel]
        procs = []
        for idx, (html_path, pdf_path) in enumerate(batch):
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            profile = os.path.join(tmpdir, "chrome-%d" % (start + idx))
            procs.append((subprocess.Popen(
                chrome_cmd(chrome, html_path, pdf_path, profile),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE), pdf_path))
        sizes = dict((pdf, (-1, 0)) for _, pdf in procs)
        ready = set()
        t0 = time.time()
        while time.time() - t0 < timeout and len(ready) < len(procs):
            for _, pdf in procs:
                if pdf in ready or not os.path.exists(pdf):
                    continue
                size = os.path.getsize(pdf)
                prev, stable = sizes[pdf]
                if size == prev and size > 0:
                    stable += 1
                    if stable >= 3:
                        ready.add(pdf)
                    sizes[pdf] = (size, stable)
                else:
                    sizes[pdf] = (size, 0)
            time.sleep(0.2)
        for proc, pdf in procs:
            _kill(proc)
            if os.path.exists(pdf) and os.path.getsize(pdf) > 0:
                done.append(pdf)
            else:
                die("Chrome не створив %s. Спробуй --лише-docx "
                    "або перевір, чи відкривається Chrome." % pdf)
    return done


def pdf_page_count(path):
    data = io.open(path, "rb").read()
    n = len(re.findall(br"/Type\s*/Page[^s]", data))
    return n if n else 1


# ------------------------------------------------------------------ pandoc DOCX

FOOTER_RID = "rId900"
FOOTER_PART = "word/footer1.xml"

A4 = ('<w:footerReference w:type="default" r:id="%s"/>'
      '<w:pgSz w:w="11906" w:h="16838"/>'
      '<w:pgMar w:top="680" w:right="680" w:bottom="620" w:left="680" '
      'w:header="340" w:footer="340" w:gutter="0"/>' % FOOTER_RID)


def _fld(instr):
    """Поле Word (PAGE, NUMPAGES) як послідовність ранів."""
    rpr = '<w:rPr><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>'
    return ('<w:r>%s<w:fldChar w:fldCharType="begin"/></w:r>'
            '<w:r>%s<w:instrText xml:space="preserve"> %s </w:instrText></w:r>'
            '<w:r>%s<w:fldChar w:fldCharType="separate"/></w:r>'
            '<w:r>%s<w:t>1</w:t></w:r>'
            '<w:r>%s<w:fldChar w:fldCharType="end"/></w:r>'
            % (rpr, rpr, instr, rpr, rpr, rpr))


FOOTER_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:p><w:pPr><w:jc w:val="center"/>'
    '<w:rPr><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr></w:pPr>'
    + _fld("PAGE")
    + '<w:r><w:rPr><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>'
      '<w:t xml:space="preserve"> / </w:t></w:r>'
    + _fld("NUMPAGES")
    + '</w:p></w:ftr>')

FOOTER_TYPE = ('<Override PartName="/word/footer1.xml" ContentType='
               '"application/vnd.openxmlformats-officedocument'
               '.wordprocessingml.footer+xml"/>')

FOOTER_REL = ('<Relationship Type="http://schemas.openxmlformats.org'
              '/officeDocument/2006/relationships/footer" Id="%s" '
              'Target="footer1.xml"/>' % FOOTER_RID)


def make_reference_docx(path):
    """Штатний reference.docx pandoc, перероблений під A4 з вузькими полями."""
    raw = subprocess.check_output(["pandoc", "--print-default-data-file",
                                   "reference.docx"])
    tmp = path + ".orig"
    io.open(tmp, "wb").write(raw)
    zin = zipfile.ZipFile(tmp, "r")
    zout = zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/document.xml":
            xml = data.decode("utf-8")
            if re.search(r"<w:pgSz[^/]*/>", xml):
                xml = re.sub(r"<w:pgSz[^/]*/>\s*(<w:pgMar[^/]*/>)?", A4, xml, count=1)
            elif re.search(r"<w:sectPr\s*/>", xml):
                xml = re.sub(r"<w:sectPr\s*/>",
                             "<w:sectPr>" + A4 + "</w:sectPr>", xml, count=1)
            elif "<w:sectPr" in xml:
                xml = re.sub(r"(<w:sectPr[^>]*>)", r"\g<1>" + A4, xml, count=1)
            data = xml.encode("utf-8")
        elif item.filename == "[Content_Types].xml":
            data = data.decode("utf-8").replace(
                "</Types>", FOOTER_TYPE + "</Types>").encode("utf-8")
        elif item.filename == "word/_rels/document.xml.rels":
            data = data.decode("utf-8").replace(
                "</Relationships>",
                FOOTER_REL + "</Relationships>").encode("utf-8")
        elif item.filename == "word/styles.xml":
            xml = data.decode("utf-8")
            xml = re.sub(r'(<w:docDefaults>.*?<w:sz w:val=")\d+(")',
                         r"\g<1>20\g<2>", xml, flags=re.S)
            data = xml.encode("utf-8")
        zout.writestr(item, data)
    zout.writestr(FOOTER_PART, FOOTER_XML.encode("utf-8"))
    zin.close(); zout.close(); os.remove(tmp)


PAGEBREAK = ("```{=openxml}\n"
             '<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n'
             "```")


LIST_RE = re.compile(r"^\s*(?:\d+[.)]\s|[-*+·]\s)")
TABLE_RE = re.compile(r"^\s*\|")
HEAD_RE = re.compile(r"^\s*#{1,6}\s")
FENCE_RE = re.compile(r"^\s*```")
TASK_MD_RE = re.compile(
    r"^(\*\*(?:Завдання|Частина|Задача|Задачі|Крок|Варіант|Бонус)[^*]*\*\*)\s*(.*)$")


def normalize_md(md):
    """Готує markdown для pandoc.

    Obsidian показує список і без порожнього рядка перед ним, pandoc — ні,
    тому такі рядки просто злипаються в абзац. Тут ці порожні рядки
    розставляються, а решта тексту не змінюється.
    """
    lines = md.split("\n")
    out = []
    in_fence = False
    for line in lines:
        if FENCE_RE.match(line):
            if not in_fence and out and out[-1].strip():
                out.append("")
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        tm = TASK_MD_RE.match(line.strip())
        if tm:
            # заголовок завдання — окремим абзацом, умова з наступного
            if out and out[-1].strip():
                out.append("")
            out.append(tm.group(1))
            out.append("")
            if tm.group(2):
                out.append(tm.group(2))
            continue

        prev = out[-1] if out else ""
        prev_blank = (not prev.strip())

        starts_block = (LIST_RE.match(line) or TABLE_RE.match(line)
                        or HEAD_RE.match(line))
        if starts_block and not prev_blank:
            same_kind = (
                (LIST_RE.match(line) and LIST_RE.match(prev)) or
                (TABLE_RE.match(line) and TABLE_RE.match(prev)))
            if not same_kind:
                out.append("")
        elif line.strip() and not starts_block and not prev_blank \
                and (LIST_RE.match(prev) or TABLE_RE.match(prev)):
            # абзац одразу після списку чи таблиці
            if not line.startswith(("  ", "\t")):
                out.append("")
        out.append(line)
    return "\n".join(out)


def build_markdown(items, name_line):
    chunks = []
    for lesson, body_md in items:
        head = [u"# %s" % lesson.heading,
                u"**%s**" % lesson.title,
                u"*Практичні завдання в зошиті*"]
        if name_line:
            head.append(u"Прізвище, ім'я \\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_ "
                        u"Дата \\_\\_\\_\\_\\_\\_\\_\\_")
        head.append(u"---")
        chunks.append("\n\n".join(head) + "\n\n" + normalize_md(body_md).strip())
    return ("\n\n" + PAGEBREAK + "\n\n").join(chunks) + "\n"


def make_docx(md_text, out_path, tmpdir):
    md_path = os.path.join(tmpdir, "zoshyt.md")
    io.open(md_path, "w", encoding="utf-8").write(md_text)
    ref = os.path.join(tmpdir, "reference.docx")
    try:
        make_reference_docx(ref)
        ref_args = ["--reference-doc=" + ref]
    except Exception as exc:
        warn("не вдалося налаштувати A4 для .docx (%s) — беру стандартний шаблон"
             % exc)
        ref_args = []
    subprocess.check_call(["pandoc", md_path, "-f", "markdown+raw_attribute",
                           "-o", out_path] + ref_args)


# ----------------------------------------------------------------------- дрібне

def info(msg):
    sys.stderr.write("   %s\n" % msg)


def warn(msg):
    sys.stderr.write("!  %s\n" % msg)


def die(msg):
    sys.stderr.write("✗  %s\n" % msg)
    sys.exit(1)


def slug(specs):
    parts = []
    for s in specs:
        course, g, sem, lo, hi = parse_spec(s)
        rng = ("%d" % lo) if lo == hi else "%d-%d" % (lo, hi)
        parts.append(("python-%s" % rng) if course == "python"
                     else ("%dкл-%s" % (g, rng)))
    return "_".join(parts)


# -------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(
        description="Роздруківки практичних завдань у зошиті (docx + pdf).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Приклад:\n  python3 zoshyt.py "5 клас 2-3 урок" "7 клас 11-12" '
               '"9 клас 2-4" "пайтон 1-5"\n\n'
               'Класи 5-9: «5 клас 2-3 урок», «7 клас 11», «6 клас ІІ 4-6».\n'
               'Курс Python (тека «Уроки/Пайтон»): «пайтон 1-5», «python 13».\n\n'
               'Кегль завжди 14 pt (без підбору) — можна змінити ключем --кегль.\n'
               'За замовчуванням робиться лише PDF. Для Word-файлу додай --docx.')
    ap.add_argument("specs", nargs="+", metavar="ЗАПИТ")
    ap.add_argument("-o", "--out", help="назва файлів без розширення")
    ap.add_argument("--відповіді", dest="answers", action="store_true",
                    help="додати блок відповідей (примірник для вчителя)")
    ap.add_argument("--підпис", dest="name_line", action="store_true",
                    help="рядок «Прізвище / Дата» вгорі сторінки")
    ap.add_argument("--кегль", dest="font", type=float, default=DEFAULT_FONT_PT,
                    help="кегль тексту в pt (типово %g)" % DEFAULT_FONT_PT)
    ap.add_argument("--docx", dest="want_docx", action="store_true",
                    help="зробити ще й .docx (за замовчуванням лише .pdf)")
    ap.add_argument("--лише-docx", dest="only_docx", action="store_true",
                    help="зробити лише .docx, без .pdf")
    args = ap.parse_args()

    make_docx_file = args.want_docx or args.only_docx
    make_pdf_file = not args.only_docx

    if make_docx_file and not shutil.which("pandoc"):
        die("немає pandoc — постав його (brew install pandoc) або не проси .docx")
    chrome = find_chrome()
    if make_pdf_file and not chrome:
        die("не знайдено Chrome — запусти з --лише-docx")

    lessons = select(scan_lessons() + scan_python_lessons(), args.specs)
    if not lessons:
        die("жодного уроку не відібрано")

    items = []
    for lesson in lessons:
        body = extract(lesson, args.answers)
        if body:
            items.append((lesson, body))
    if not items:
        die("у відібраних уроках немає блоків «У зошиті»")

    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    base = args.out or ("Зошит " + slug(args.specs))
    tmpdir = os.path.join(OUT_DIR, ".tmp")
    if not os.path.isdir(tmpdir):
        os.makedirs(tmpdir)

    sys.stderr.write("Уроків відібрано: %d\n" % len(items))
    for lesson, _ in items:
        info("%s · %s" % (lesson.heading, lesson.title))

    made = []

    if make_pdf_file:
        info("кегль: %g pt" % args.font)
        pages = [page_html(lesson, md_to_html(body_md), args.font,
                           args.name_line)
                 for lesson, body_md in items]
        html_path = os.path.join(tmpdir, "zoshyt.html")
        io.open(html_path, "w", encoding="utf-8").write(
            document_html(pages, base))
        pdf_path = os.path.join(OUT_DIR, base + ".pdf")
        render_pdfs(chrome, [(html_path, pdf_path)], tmpdir)
        made.append((pdf_path, pdf_page_count(pdf_path)))

    if make_docx_file:
        docx_path = os.path.join(OUT_DIR, base + ".docx")
        make_docx(build_markdown(items, args.name_line), docx_path, tmpdir)
        made.append((docx_path, None))

    sys.stderr.write("\nГотово:\n")
    for path, pages in made:
        extra = (" · сторінок: %d" % pages) if pages else ""
        sys.stderr.write("   %s%s\n" % (path, extra))


if __name__ == "__main__":
    main()
