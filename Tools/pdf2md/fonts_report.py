# -*- coding: utf-8 -*-
"""
fonts_report.py — інвентаризація шрифтів у PDF-підручнику.

ЗАВЖДИ запускай це ПЕРШИМ, коли береш новий підручник: pidruchnyk2md.py визначає ролі
елементів (заголовок / рубрика / підпис / тіло тексту) за іменами шрифтів верстки,
і саме цей звіт показує, які імена та кеглі треба вписати у role_of() та skip_block().

    python3 fonts_report.py книга.pdf            # звіт по шрифтах
    python3 fonts_report.py книга.pdf 42 43      # детальний дамп сторінок 42 і 43

Що шукати у звіті:
  • шрифт з найбільшою кількістю символів — це тіло тексту;
  • окремий «гротеск» (AvantGarde, Arial Narrow тощо) — заголовки та назви рубрик,
    різні кеглі = різні рівні; найдрібніший кегль зазвичай колонтитул (його викидаємо);
  • Symbol / Wingdings / Garamond — значки маркерів списків;
  • якщо трапляється Times New Roman 14 — частину книжки зверстано у Word,
    її обробляє окремий режим regime="times".
"""
import collections
import sys

import pymupdf


def report(path):
    doc = pymupdf.open(path)
    print(f"Сторінок: {doc.page_count}")
    sizes = collections.Counter()
    for pno in range(doc.page_count):
        sizes[tuple(round(x) for x in doc[pno].rect[2:])] += 1
    print("Розміри сторінок (pt):", sizes.most_common())
    cnt, samples = collections.Counter(), collections.defaultdict(list)
    for pno in range(doc.page_count):
        for b in doc[pno].get_text("dict")["blocks"]:
            if b["type"] != 0:
                continue
            for line in b["lines"]:
                for sp in line["spans"]:
                    t = sp["text"].strip()
                    if not t:
                        continue
                    key = (sp["font"], round(sp["size"], 1))
                    cnt[key] += len(t)
                    if len(samples[key]) < 3:
                        samples[key].append(f"с.{pno}: {t[:70]}")
    for key, n in cnt.most_common():
        print(f"\n{key[0]}  {key[1]}pt  — {n} симв.")
        for x in samples[key]:
            print("    ", x)


def dump(path, pages):
    doc = pymupdf.open(path)
    for pno in pages:
        page = doc[pno]
        print(f"===== сторінка {pno}  {page.rect}")
        for bi, b in enumerate(page.get_text("dict")["blocks"]):
            if b["type"] != 0:
                print(f" [ЗОБРАЖЕННЯ {bi}] {[round(x) for x in b['bbox']]}")
                continue
            print(f" [БЛОК {bi}] {[round(x) for x in b['bbox']]}")
            for line in b["lines"]:
                txt = "".join(s["text"] for s in line["spans"])
                fonts = sorted({(s["font"], round(s["size"], 1)) for s in line["spans"]})
                print(f"   x0={round(line['bbox'][0])} x1={round(line['bbox'][2])} "
                      f"y={round(line['bbox'][1])} {fonts}\n      | {txt}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if len(sys.argv) > 2:
        dump(sys.argv[1], [int(x) for x in sys.argv[2:]])
    else:
        report(sys.argv[1])
