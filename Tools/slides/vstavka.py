"""Дописати слайди в уже готову HTML-колоду, для якої немає скрипта-генератора (зроблену раніше вручну).

    from vstavka import patch_deck
    def build(d):                      # d — тимчасова Deck; робимо слайди як звичайно (без s.frame!)
        s = d.slide("Нова назва", "нотатки"); ...
    patch_deck(path, after="Назва наявного слайда", build=build, fixes=[("стара фраза", "нова")])

Що робить:
  * вставляє нові <section> після слайда з data-label == after (якщо слайда з такою назвою ще немає — повторний
    запуск нічого не дублює);
  * перенумеровує id="N" і «Slide N of T» (навігація рушія йде за порядком секцій);
  * дописує записи в JSON deck-motion (по одному на новий слайд);
  * fixes — заміни тексту по всьому файлу (наприклад, назви пунктів меню);
  * replace=True — якщо слайди з такими назвами вже є, перезібрати їх на місці (напр. після нових скрінів).
Кліки-появи (s.frame) у вставлених слайдах не підтримано: їхні id перетнулися б з наявними.
"""
import json
import re

from deck import Deck


def patch_deck(path, after=None, build=None, fixes=(), kind="info", topic="", replace=False):
    html = open(path, encoding="utf-8").read()
    for old, new in fixes:
        html = html.replace(old, new)
    if build is not None:
        d = Deck("tmp", kind=kind, topic=topic)
        build(d)
        a = html.index("<main")
        a = html.index(">", a) + 1
        b = html.index("</main>")
        head, body, tail = html[:a], html[a:b], html[b:]
        starts = [m.start() for m in re.finditer(r'<section class="deck-slide"', body)]
        secs = [body[s:e] for s, e in zip(starts, starts[1:] + [len(body)])]
        pre = body[:starts[0]]
        labels = [re.search(r'data-label="([^"]*)"', s).group(1) for s in secs]
        new_labels = [s.label for s in d.slides]
        m = re.search(r'(<script type="application/json" id="deck-motion">)(.*?)(</script>)', head, flags=re.S)
        if replace and all(l in labels for l in new_labels):
            for s in d.slides:
                assert not s.frames, "у вставлених слайдах не можна s.frame()"
            motion = json.loads(m.group(2))
            for s in d.slides:
                k = labels.index(s.label)
                secs[k] = s.render(0) + "\n"
                motion["slides"][k] = s.motion()
            mj = json.dumps(motion, ensure_ascii=False, separators=(",", ":"))
            head = head[:m.start(2)] + mj + head[m.end(2):]
        elif not any(l in labels for l in new_labels):
            for s in d.slides:
                assert not s.frames, "у вставлених слайдах не можна s.frame()"
            k = labels.index(after) + 1
            new_secs = [s.render(0) + "\n" for s in d.slides]
            secs = secs[:k] + new_secs + secs[k:]
            motion = json.loads(m.group(2))
            motion["slides"][k:k] = [s.motion() for s in d.slides]
            mj = json.dumps(motion, ensure_ascii=False, separators=(",", ":"))
            head = head[:m.start(2)] + mj + head[m.end(2):]
        total = len(secs)
        out = []
        for i, sec in enumerate(secs, 1):
            sec = re.sub(r'(<section class="deck-slide" id=")\d+(")', rf"\g<1>{i}\2", sec, count=1)
            sec = re.sub(r'aria-label="Slide \d+ of \d+"', f'aria-label="Slide {i} of {total}"', sec, count=1)
            out.append(sec)
        html = head + pre + "".join(out) + tail
    open(path, "w", encoding="utf-8").write(html)
    return path
