"""Python, урок 25. Полотно Canvas: вікно, координати, фігури."""
import os
from deck import Deck, c, esc, shot, REPO, INK, INK2, ORANGE, BLUE, DARK_BG, PAPER
from grafika import prog

d = Deck("Полотно Canvas", kind="python", topic="Полотно Canvas")


def at(o, cx, cy):
    ox, oy, k = o
    return ox + (cx + 1) * k, oy + (cy + 1) * k


# 1 — титул
full = prog('''
полотно.create_rectangle(0, 300, 600, 400, fill="lightgreen", outline="")
полотно.create_oval(460, 40, 560, 140, fill="gold", outline="orange", width=4)
полотно.create_rectangle(120, 180, 300, 320, fill="lightyellow", outline="black", width=2)
полотно.create_polygon(100, 180, 210, 90, 320, 180, fill="brown", outline="black", width=2)
полотно.create_rectangle(190, 240, 235, 320, fill="saddlebrown")
полотно.create_line(380, 320, 380, 230, fill="sienna", width=10)
полотно.create_oval(330, 160, 430, 260, fill="forestgreen", outline="")
полотно.create_text(300, 370, text="Мій перший малюнок", font=("Arial", 20), fill="darkgreen")
''', title="Полотно")
s = d.title("Python", "Полотно Canvas", "Фігури за координатами",
            notes="Сьогодні знайомимося з новим інструментом — полотном tkinter. На ньому фігури не малюють рухом, як черепашка, "
                  "а ставлять одразу цілими за координатами. Наприкінці уроку кожен намалює ось таку картинку — і навіть кращу.")
s.window(1180, 150, 600, shot(full))

# 2 — план
d.plan(["Чому не черепашка?", "Вікно з полотном", "Координати: де нуль?", "Знайди точку",
        "Прямокутник за двома кутами", "Овал у невидимій рамці", "Лінія й ламана", "Текст на полотні",
        "Кольори", "Збираємо малюнок", "Помилки й практика"],
       notes="Сьогодні багато малювання. Кожен приклад на слайдах — справжній скриншот того, що покаже програма.")

# 3 — гачок
s = d.slide("Чому не черепашка?",
            "Черепашка малює як людина з олівцем: іде й лишає слід. Посунути вже намальований квадрат вона не вміє — "
            "для неї це просто пікселі. А в іграх усе рухається. Тому беремо полотно: тут кожна фігура — окремий предмет, "
            "який можна посунути, перефарбувати чи стерти. Це знадобиться через два уроки.")
s.h2("Чому не черепашка?")
s.sub("Черепашка вміє малювати. Але посунути намальоване — ні.")
s.card(128, 310, 800, 420, "Черепашка", ["малює рухом: іде й лишає слід",
                                         "намальоване — просто пікселі",
                                         "посунути квадрат? Тільки стерти все й перемалювати"],
       kind="light", title_size=44, body_size=32, valign="flex-start")
with s.frame():
    s.card(992, 310, 800, 420, "Полотно", ["ставить фігуру одразу цілою",
                                           "кожна фігура запам’ятовується",
                                           "її можна посунути, перефарбувати, стерти"],
           kind="blue", title_size=44, body_size=32, valign="flex-start")
with s.frame("pop"):
    s.note(800, "Полотно — основа для анімації та ігор. Сьогодні вчимося на ньому малювати.", size=34)

# 4 — вікно
win = '''import tkinter

вікно = tkinter.Tk()
вікно.title("Малюємо на полотні")

полотно = tkinter.Canvas(вікно, width=600,
                         height=400, bg="white")
полотно.pack()

вікно.mainloop()'''
s = d.slide("Вікно з полотном",
            "П’ять рядків, які будуть на початку кожної графічної програми. Tk() створює вікно, Canvas — полотно всередині нього, "
            "pack() ставить полотно у вікно, mainloop() тримає вікно відкритим. Без mainloop вікно блимне й зникне.")
s.h2("Вікно з полотном")
s.code(128, 214, 990, 520, win, size=27)
o = s.window(1150, 214, 642, shot(win))
items = [("Tk()", "створює вікно"), ("Canvas(…)", "полотно: ширина, висота, фон"), ("pack()", "ставить полотно у вікно"),
         ("mainloop()", "тримає вікно відкритим")]
for k, (cmd, what) in enumerate(items):
    with s.frame():
        x = 128 + (k % 2) * 490
        y = 760 + (k // 2) * 120
        s.box(x, y, 470, 100, "blue" if k == 3 else "light", radius=16)
        s.text(x + 24, y, 200, 100, esc(cmd), size=26, weight=700, mono=True, color=BLUE, valign="center")
        s.text(x + 220, y, 236, 100, what, size=24, valign="center", lh=1.2)
with s.frame():
    s.text(1130, 760, 662, 200, "Порожнє біле полотно 600 × 400 — наш аркуш.", size=30, weight=600)

# 5 — координати
s = d.slide("Координати: де нуль?",
            "Найважливіше на уроці. На полотні нуль — у лівому верхньому куті. x росте праворуч, y росте ВНИЗ, не вгору, як у математиці. "
            "У черепашки нуль був у центрі. Питаємо: де точка (600, 400)? У правому нижньому куті.")
s.h2("Координати: де нуль?")
s.sub("Нуль — у лівому верхньому куті. y росте <b>вниз</b>.")
gx, gy, gw, gh = 200, 320, 900, 600
s.raw(f'<div style="position:absolute;left:{gx}px;top:{gy}px;width:{gw}px;height:{gh}px;background:#fff;'
      f'border:2px solid {DARK_BG};background-image:linear-gradient(#E3E8EE 2px,transparent 2px),'
      f'linear-gradient(90deg,#E3E8EE 2px,transparent 2px);background-size:75px 75px"></div>')
s.raw(f'<svg style="position:absolute;left:0px;top:0px" width="1920" height="1080" viewBox="0 0 1920 1080">'
      f'<defs><marker id="ax" markerWidth="14" markerHeight="14" refX="10" refY="7" orient="auto">'
      f'<path d="M0,0 L14,7 L0,14 z" fill="{BLUE}"/></marker></defs>'
      f'<path d="M{gx} {gy - 30} L{gx + gw + 60} {gy - 30}" stroke="{BLUE}" stroke-width="5" marker-end="url(#ax)"/>'
      f'<path d="M{gx - 30} {gy} L{gx - 30} {gy + gh + 50}" stroke="{BLUE}" stroke-width="5" marker-end="url(#ax)"/></svg>')
s.text(gx + gw + 70, gy - 56, 60, 50, "x", size=40, weight=700, color=BLUE, mono=True)
s.text(gx - 50, gy + gh + 40, 60, 50, "y", size=40, weight=700, color=BLUE, mono=True)
s.marker(gx, gy, "(0, 0)", color=ORANGE, side="left")
with s.frame():
    s.marker(gx + 450, gy + 225, "(300, 150)", color=BLUE)
with s.frame():
    s.marker(gx + gw, gy + gh, "(600, 400)", color=ORANGE, side="left")
with s.frame():
    s.card(1240, 320, 552, 280, "Не як у математиці!", ["y = 0 — це <b>верх</b> полотна.", "Що більше y — то нижче точка."],
           kind="orange", title_size=34, body_size=30, valign="flex-start")
with s.frame():
    s.card(1240, 640, 552, 280, "А в черепашки?", ["Нуль був у центрі, і y ріс угору.", "Тут — інакше."],
           kind="light", title_size=34, body_size=30, valign="flex-start")

# 6 — знайди точку
s = d.slide("Знайди точку",
            "Гра на швидкість. Показуємо точку — клас називає координати. Полотно 600 × 400, клітинка — 50. "
            "Відповіді відкриваються кліком. Потім навпаки: називаємо координати, учень показує на дошці.")
s.h2("Знайди точку")
s.sub("Полотно 600 × 400, одна клітинка — 50 точок.")
gx, gy, gw, gh, k = 128, 300, 960, 640, 1.6
s.raw(f'<div style="position:absolute;left:{gx}px;top:{gy}px;width:{gw}px;height:{gh}px;background:#fff;'
      f'border:2px solid {DARK_BG};background-image:linear-gradient(#E3E8EE 2px,transparent 2px),'
      f'linear-gradient(90deg,#E3E8EE 2px,transparent 2px);background-size:80px 80px"></div>')
pts = [("A", 100, 50), ("B", 500, 100), ("C", 250, 300), ("D", 50, 350)]
for name, x, y in pts:
    px, py = gx + x * k, gy + y * k
    s.raw(f'<div style="position:absolute;left:{px - 14}px;top:{py - 14}px;width:28px;height:28px;border-radius:50%;'
          f'background:{BLUE}"></div>')
    s.text(int(px + 18), int(py - 50), 60, 40, name, size=34, weight=800, color=BLUE)
for i, (name, x, y) in enumerate(pts):
    s.text(1160, 320 + i * 150, 120, 110, f"<b>{name}</b>", size=48, color=BLUE, valign="center")
    with s.frame("pop"):
        s.chip(1260, 320 + i * 150, 532, 110, f"({x}, {y})", kind="blue", size=40)

# 7 — прямокутник
rect = 'полотно.create_rectangle(50, 50, 250, 150, fill="yellow", outline="black", width=3)'
s = d.slide("Прямокутник за двома кутами",
            "Прямокутник задають двома кутами: лівим верхнім (x1, y1) і правим нижнім (x2, y2). "
            "Ширина — це x2 − x1 = 200, висота — y2 − y1 = 100. Параметри fill, outline, width необов’язкові.")
s.h2("Прямокутник за двома кутами")
s.code(128, 214, 1664, 120, rect, size=27, framed=False)
o = s.window(128, 370, 900, shot(prog(rect)))
with s.frame():
    s.marker(*at(o, 50, 50), "(50, 50)", side="left")
with s.frame():
    s.marker(*at(o, 250, 150), "(250, 150)")
with s.frame():
    s.card(1080, 370, 712, 250, "Лівий верхній → правий нижній",
           [c("x1, y1") + " — один кут, " + c("x2, y2") + " — протилежний."], kind="blue", title_size=32, body_size=29)
with s.frame():
    s.table(1080, 650, [300, 408], [["параметр", "що робить"], ["fill", "колір заливки"], ["outline", "колір контуру"],
                                    ["width", "товщина контуру"]], row_h=66, size=28)

# 8 — овал
oval = '''полотно.create_rectangle(50, 50, 250, 150, outline="gray", dash=(6, 4))
полотно.create_oval(50, 50, 250, 150, fill="red")
полотно.create_rectangle(320, 50, 470, 200, outline="gray", dash=(6, 4))
полотно.create_oval(320, 50, 470, 200, fill="dodgerblue")'''
s = d.slide("Овал у невидимій рамці",
            "Овал задають так само, як прямокутник: двома кутами рамки, у яку він вписаний. Сіра пунктирна рамка — лише для пояснення, "
            "у справжній програмі її немає. Якщо рамка квадратна, вийде коло. Питаємо: як намалювати коло радіусом 50 з центром у (300, 200)?")
s.h2("Овал у невидимій рамці")
s.code(128, 214, 1664, 210, oval, size=25, framed=False)
s.window(128, 460, 780, shot(prog(oval)))
with s.frame():
    s.card(980, 460, 812, 200, "Рамка прямокутна", "вийде овал", kind="light", title_size=34, body_size=30)
with s.frame():
    s.card(980, 690, 812, 200, "Рамка квадратна", "вийде коло: ширина = висоті", kind="blue", title_size=34,
           body_size=30)
with s.frame():
    s.text(980, 920, 812, 100, "Коло з центром (300, 200) і радіусом 50: " + c("create_oval(250, 150, 350, 250)"),
           size=26, weight=600)

# 9 — лінія
line = '''полотно.create_line(0, 0, 600, 400, fill="blue", width=2)
полотно.create_line(50, 350, 150, 250, 250, 350, 350, 250, 450, 350, fill="green", width=6)'''
s = d.slide("Лінія й ламана",
            "Лінія — від точки до точки. Якщо дати більше пар чисел, вийде ламана: Python з’єднає всі точки по черзі. "
            "Друга лінія тут — п’ять точок, зигзаг.")
s.h2("Лінія й ламана")
s.code(128, 214, 1664, 170, line, size=25, framed=False)
o = s.window(128, 420, 820, shot(prog(line)))
with s.frame():
    for (x, y) in [(50, 350), (150, 250), (250, 350), (350, 250), (450, 350)]:
        sx, sy = at(o, x, y)
        s.raw(f'<div style="position:absolute;left:{sx - 10}px;top:{sy - 10}px;width:20px;height:20px;border-radius:50%;'
              f'background:{ORANGE};border:3px solid #fff"></div>')
with s.frame():
    s.card(980, 420, 812, 230, "Дві точки — лінія", c("create_line(x1, y1, x2, y2)"), kind="light", title_size=34,
           body_size=27)
with s.frame():
    s.card(980, 680, 812, 230, "Більше точок — ламана", "Точки з’єднуються по черзі.", kind="blue", title_size=34,
           body_size=30)

# 10 — текст
txt = '''полотно.create_text(300, 60, text="Мій малюнок", font=("Arial", 32), fill="navy")
полотно.create_text(300, 200, text="центр тексту — тут", font=("Arial", 20))
полотно.create_oval(295, 195, 305, 205, fill="red")'''
s = d.slide("Текст на полотні",
            "Текст ставлять за координатами його ЦЕНТРУ — червона точка показує, де саме. Тому create_text(300, …) — "
            "текст рівно посередині полотна шириною 600. font — шрифт і розмір, fill — колір.")
s.h2("Текст на полотні")
s.code(128, 214, 1664, 210, txt, size=25, framed=False)
s.window(128, 460, 780, shot(prog(txt)))
with s.frame():
    s.card(980, 460, 812, 220, "Координати — це центр", "Червона точка: саме туди ставиться середина тексту.",
           kind="orange", title_size=34, body_size=29)
with s.frame():
    s.card(980, 710, 812, 220, "Шрифт", c('font=("Arial", 32)') + " — назва і розмір", kind="light", title_size=34,
           body_size=29)

# 11 — кольори
cols = ["red", "orange", "gold", "green", "dodgerblue", "purple", "pink", "brown", "gray", "#2F6FB7", "#F0A55E", "#3E3F42"]
body = "\n".join(
    f'полотно.create_rectangle({20 + (i % 4) * 145}, {20 + (i // 4) * 125}, {145 + (i % 4) * 145}, {120 + (i // 4) * 125}, '
    f'fill="{cname}")\nполотно.create_text({82 + (i % 4) * 145}, {70 + (i // 4) * 125}, text="{cname}", fill="white", '
    f'font=("Arial", 14, "bold"))' for i, cname in enumerate(cols))
s = d.slide("Кольори",
            "Колір пишуть англійською назвою в лапках або кодом з решіткою: #RRGGBB — скільки червоного, зеленого й синього. "
            "Назв у tkinter сотні: lightgreen, skyblue, saddlebrown, gold… Якщо назву написати з помилкою, Python скаже unknown color name.")
s.h2("Кольори")
s.sub("Назва англійською — або код " + c("#RRGGBB") + ".")
s.window(128, 300, 900, shot(prog(body, h=390)))
with s.frame():
    s.card(1080, 300, 712, 230, "Назвою", c('fill="gold"') + ", " + c('"skyblue"') + ", " + c('"saddlebrown"'),
           kind="light", title_size=34, body_size=27)
with s.frame():
    s.card(1080, 560, 712, 230, "Кодом", c('fill="#2F6FB7"') + " — червоний, зелений, синій від 00 до FF", kind="blue",
           title_size=34, body_size=27)
with s.frame():
    s.card(1080, 820, 712, 160, None, "Помилка в назві → " + c("unknown color name"), kind="orange", body_size=28)

# 12 — збираємо малюнок: світлофор і смайлик
light = '''полотно.create_rectangle(80, 40, 200, 360, fill="#3E3F42")
полотно.create_oval(100, 60, 180, 140, fill="red")
полотно.create_oval(100, 160, 180, 240, fill="gray")
полотно.create_oval(100, 260, 180, 340, fill="gray")

полотно.create_oval(300, 80, 540, 320, fill="gold")
полотно.create_oval(360, 150, 390, 190, fill="black")
полотно.create_oval(450, 150, 480, 190, fill="black")
полотно.create_line(370, 250, 420, 280, 470, 250,
                    width=6, smooth=True)'''
s = d.slide("Збираємо малюнок",
            "Будь-який малюнок — це прості фігури. Світлофор — прямокутник і три кола. Смайлик — велике коло, два овали-очі й ламана-усмішка "
            "з параметром smooth=True, який згладжує кути. Фігури малюються по черзі: пізніша лягає зверху.")
s.h2("Збираємо малюнок")
s.code(128, 214, 1000, 530, light, size=26, lh=1.45, framed=False)
s.window(1160, 214, 632, shot(prog(light, title="Світлофор і смайлик")))
with s.frame():
    s.card(1160, 690, 632, 190, "Хто зверху?", "Що намалювали пізніше — те лягає поверх.", kind="blue", title_size=32,
           body_size=28)
with s.frame():
    s.card(128, 770, 1000, 150, None, c("smooth=True") + " згладжує ламану — і зигзаг стає усмішкою.", kind="light",
           body_size=28)

# 13 — що намалює
qs = ['полотно.create_rectangle(\n    100, 100, 500, 300,\n    fill="blue")',
      'полотно.create_oval(\n    200, 100, 400, 300,\n    fill="green")',
      'полотно.create_line(\n    0, 200, 600, 200, width=8)\nполотно.create_line(\n    300, 0, 300, 400, width=8)']
s = d.slide("Що намалює програма?",
            "Клас малює відповідь на листочку чи в повітрі, потім відкриваємо справжній результат. "
            "Друга — коло, бо рамка 200 на 200. Третя — хрест посередині.")
s.h2("Що намалює програма?")
for k, q in enumerate(qs):
    x = 128 + k * 568
    s.code(x, 230, 528, 210, q, size=24, framed=False)
for k, q in enumerate(qs):
    x = 128 + k * 568
    with s.frame("pop"):
        s.window(x, 470, 524, shot(prog(q)), title="Відповідь")

# 14 — типові помилки
s = d.slide("Типові помилки",
            "Перша — забули pack(): вікно відкривається, але полотна в ньому немає. Друга — забули mainloop(): вікно блимає й зникає. "
            "Третя — колір з помилкою: unknown color name. Четверта — плутають висоту з y: прямокутник вилазить за низ.")
s.text(128, 420, 560, 240, "Типові<br/>помилки", size=96, weight=700, lh=1.02, extra=";letter-spacing:-3px")
s.text(128, 860, 540, 120, "Python скаже лише про колір. Решту видно тільки по вікну.", size=26, color=INK2, lh=1.35)
with s.frame():
    s.mistake(720, 130, 1072, '''полотно = tkinter.Canvas(вікно, width=600, height=400)
# забули полотно.pack()''', "Без " + c("pack()") + " полотна у вікні не буде", code_h=110, size=24)
with s.frame():
    s.mistake(720, 370, 1072, '''полотно.create_oval(10, 10, 90, 90)
# забули вікно.mainloop()''', "Без " + c("mainloop()") + " вікно блимне й зникне", code_h=110, size=24)
with s.frame():
    s.mistake(720, 610, 1072, '''полотно.create_rectangle(10, 10, 90, 90, fill="yelow")''',
              c("unknown color name") + ": колір з помилкою", code_h=80, size=24)
with s.frame():
    s.mistake(720, 820, 1072, '''полотно.create_rectangle(50, 300, 150, 500)''',
              "Друге число — " + c("y") + " кута, а не висота: вилізли за низ", code_h=80, size=24)

# 15 — ваш хід
d.your_turn([("star", "Мішень із п’яти кіл"), ("lightning", "Світлофор, що світить зеленим"),
             ("home", "Мій перший малюнок: хатинка, сонце, підпис"), ("clock", "Без комп’ютера: фігури на клітинках")],
            notes="Три завдання за комп’ютером і одне в зошиті. Підказка для мішені: кола від найбільшого до найменшого, "
                  "бо кожне наступне лягає зверху.")

# 16 — завдання 1
target = '''полотно.create_oval(100, 0, 500, 400, fill="red")
полотно.create_oval(140, 40, 460, 360, fill="white")
полотно.create_oval(180, 80, 420, 320, fill="red")
полотно.create_oval(220, 120, 380, 280, fill="white")
полотно.create_oval(260, 160, 340, 240, fill="red")'''
s = d.task("Завдання 1. Мішень",
           "Кожне наступне коло на 40 точок менше з кожного боку. Порядок важливий: від найбільшого до найменшого. "
           "Сильнішим — зробити те саме циклом: for i in range(5) і координати через i * 40.")
s.steps(["Намалюйте п’ять кіл з одним центром — у центрі полотна (300, 200).",
         "Кожне наступне — на 40 точок менше з кожного боку.",
         "Чергуйте кольори: червоний, білий, червоний…",
         "Подумайте: чому малювати треба від <b>найбільшого</b> кола?",
         "⭐ Зробіть те саме циклом " + c("for") + "."], w=860, size=31)
s.window(1060, 216, 732, shot(prog(target, title="Мішень")), title="Мішень — зразок")

# 17 — завдання 2-3
s = d.task("Завдання 2–3. Світлофор і мій малюнок",
           "Світлофор: зелене світло знизу — третє коло fill=\"green\", решта сірі. Малюнок оцінюємо за кількістю різних фігур "
           "і охайністю координат.")
s.steps(["<b>Світлофор:</b> прямокутник і три кола. Увімкніть <b>зелене</b> світло, решту зробіть сірими.",
         "<b>Мій малюнок:</b> хатинка, сонце, трава, дерево — щонайменше 6 фігур.",
         "Використайте всі чотири команди: " + c("rectangle") + ", " + c("oval") + ", " + c("line") + ", " + c("text") + ".",
         "Унизу — підпис автора через " + c("create_text") + "."], w=860, size=31)
s.window(1060, 216, 732, shot(full), title="Приклад малюнка")

# 18 — без комп'ютера
s = d.task("Без комп’ютера: фігури на клітинках",
           "Відповіді: 1) прямокутник від (100, 50) до (300, 150) — ширина 200, висота 100; 2) коло з центром (200, 200) радіусом 50 — "
           "create_oval(150, 150, 250, 250); 3) лінія з лівого нижнього кута в правий верхній — create_line(0, 400, 600, 0).",
           where="У зошиті")
s.steps(["Накресліть полотно 12 × 8 клітинок: одна клітинка — 50 точок. Позначте (0, 0) і напрямки x та y.",
         "Намалюйте на клітинках: " + c("create_rectangle(100, 50, 300, 150)") + ".",
         "Запишіть команду для кола з центром (200, 200) і радіусом 50.",
         "Запишіть команду для лінії з лівого нижнього кута в правий верхній."], w=1000, size=30)
s.raw(f'<div style="position:absolute;left:1220px;top:230px;width:572px;height:382px;background:#fff;'
      f'border:2px solid {DARK_BG};background-image:linear-gradient(#E3E8EE 2px,transparent 2px),'
      f'linear-gradient(90deg,#E3E8EE 2px,transparent 2px);background-size:47.6px 47.6px"></div>')
s.text(1220, 630, 572, 50, "12 × 8 клітинок, клітинка = 50", size=26, weight=600, align="center", color=INK2)

out = os.path.join(REPO, "Презентації уроків", "Python", "Урок 25. Полотно Canvas.html")
print(d.save(out), len(d.slides))
