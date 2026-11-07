"""Python, урок 23. Черепашка: перші кроки (найпростіше знайомство з графікою, один цикл for)."""
import os
from deck import Deck, c, esc, shot, REPO, INK, INK2, ORANGE, BLUE, DARK_BG, PAPER

# менше вікно й товстіша лінія — щоб на проєкторі фігури було добре видно
os.environ["TURTLE_SIZE"] = "[480, 360]"
os.environ["TURTLE_PEN"] = "3"

d = Deck("Черепашка: перші кроки", kind="python", topic="Черепашка: перші кроки")


def t(body, bg=None, hide=False):
    pre = 'import turtle\n\nturtle.shape("turtle")\n'
    if bg:
        pre += f'turtle.bgcolor("{bg}")\n'
    end = "\nturtle.hideturtle()" if hide else ""
    return pre + body.strip() + end + "\n\nturtle.done()\n"


def poly(n, side, color="dodgerblue", width=4):
    return (f'turtle.pencolor("{color}")\nturtle.pensize({width})\n'
            f'for i in range({n}):\n    turtle.forward({side})\n    turtle.right({round(360 / n, 2):g})')


STAR = '''turtle.pencolor("orange")
turtle.pensize(4)
for i in range(5):
    turtle.forward(200)
    turtle.right(144)'''

SUN = '''turtle.pencolor("gold")
turtle.bgcolor("midnightblue")
for i in range(36):
    turtle.forward(220)
    turtle.right(170)'''

# 1 — титул
title_pic = '''turtle.bgcolor("midnightblue")
turtle.pensize(3)
turtle.penup()
turtle.goto(-110, 60)
turtle.pendown()
turtle.pencolor("gold")
for i in range(36):
    turtle.forward(220)
    turtle.right(170)'''
s = d.title("Python", "Черепашка: перші кроки", "Команди, кроки й кут",
            notes="Сьогодні перше знайомство з графікою на Python. По екрану повзе черепашка з пензликом на хвості й малює все, що ми їй накажемо. "
                  "Наприкінці уроку кожен намалює ось таке сонечко — трьома рядками коду.")
s.window(1180, 150, 600, shot(t(title_pic, hide=True)), title="Черепашка")

# 2 — план
d.plan(["Черепашка з пензликом", "Перший крок: forward", "Поворот: right і left", "Квадрат командами",
        "Жива черепашка", "Колір і товщина", "Цикл for: менше рядків", "Кроки: розмір фігури",
        "Кут: яка вийде фігура", "Зірка й сонечко", "Помилки й практика"],
       notes="Нових команд небагато: forward, right, left, pencolor, pensize. І знайомий цикл for.")

# 3 — гачок
s = d.slide("Черепашка з пензликом",
            "Уявіть черепашку з пензликом на хвості. Вона стоїть у центрі аркуша й дивиться праворуч. "
            "Ми кажемо: «пройди 100 кроків» — і за нею лишається лінія. «Поверни праворуч» — і вона розвертається на місці. "
            "Цю ідею придумали ще в 1960-х, щоб діти вчилися програмувати, малюючи.")
s.h2("Черепашка з пензликом")
s.sub("Вона повзе по екрану — і за нею лишається слід.")
s.card(128, 320, 520, 330, "Іде вперед", ["лишає лінію за собою"], kind="blue", title_size=40, body_size=30,
       valign="flex-start")
with s.frame():
    s.card(700, 320, 520, 330, "Повертає", ["на місці, на скільки градусів скажемо"], kind="light", title_size=40,
           body_size=30, valign="flex-start")
with s.frame():
    s.card(1272, 320, 520, 330, "Слухає команди", ["рівно ті, що ми написали, — і нічого більше"], kind="orange",
           title_size=40, body_size=30, valign="flex-start")
with s.frame():
    s.note(740, "Черепашку придумали для дітей понад 50 років тому — щоб учитися програмувати, малюючи.", size=32)

# 4 — перший крок
first = 'turtle.forward(200)'
s = d.slide("Перший крок: forward",
            "Три обов’язкові речі: import turtle на початку, команди посередині, turtle.done() наприкінці — щоб вікно не закрилося. "
            "shape(\"turtle\") лише робить курсор схожим на черепашку. forward(200) — пройти 200 кроків уперед.")
s.h2("Перший крок: forward")
s.code(128, 214, 960, 420, t(first).strip(), size=30)
s.window(1150, 214, 560, shot(t(first)), title="Перший крок")
with s.frame():
    s.table(128, 700, [440, 1224], [["рядок", "що робить"], ["import turtle", "підключає черепашку"],
                                    ["turtle.forward(200)", "200 кроків уперед — лишає лінію"],
                                    ["turtle.done()", "тримає вікно відкритим"]], row_h=72, size=28)

# 5 — поворот
s = d.slide("Поворот: right і left",
            "right — поворот праворуч, left — ліворуч, на скільки градусів. Показуємо руками: 90 — чверть оберту, «за рогом», "
            "180 — розвернутися назад, 360 — повний оберт і знову дивишся туди ж. Черепашка повертається на місці, нічого не малюючи.")
s.h2("Поворот: right і left")
s.sub("Число — це <b>градуси</b>. Черепашка повертається на місці.")
angles = [(45, "трохи"), (90, "за ріг"), (180, "назад"), (360, "повний оберт")]
for k, (a, w) in enumerate(angles):
    with s.frame():
        x = 128 + k * 420
        s.box(x, 320, 392, 400, "blue" if a == 90 else "light")
        cx, cy, r = x + 196, 500, 110
        import math
        ex = cx + r * math.cos(math.radians(a))
        ey = cy + r * math.sin(math.radians(a))
        large = 1 if a > 180 else 0
        arc = (f'<path d="M{cx + 60} {cy} A60 60 0 {large} 1 {cx + 60 * math.cos(math.radians(a - 0.01)):.1f} '
               f'{cy + 60 * math.sin(math.radians(a - 0.01)):.1f}" fill="none" stroke="{ORANGE}" stroke-width="5"/>')
        s.raw(f'<svg style="position:absolute;left:0px;top:0px" width="1920" height="1080" viewBox="0 0 1920 1080">'
              f'<defs><marker id="ar{k}" markerWidth="12" markerHeight="12" refX="9" refY="6" orient="auto">'
              f'<path d="M0,0 L12,6 L0,12 z" fill="{INK}"/></marker></defs>'
              f'<path d="M{cx} {cy} L{cx + r} {cy}" stroke="#9AA3AE" stroke-width="5" stroke-dasharray="10 8"/>'
              f'<path d="M{cx} {cy} L{ex:.1f} {ey:.1f}" stroke="{INK}" stroke-width="6" marker-end="url(#ar{k})"/>'
              f'{arc}</svg>')
        s.text(x, 640, 392, 50, f"<b>right({a})</b> — {w}", size=28, align="center", mono=False)
with s.frame():
    s.card(128, 770, 1664, 130, None, c("right") + " — праворуч, " + c("left") + " — ліворуч. Покажіть рукою: куди повернеться?",
           kind="orange", body_size=32, align="center")

# 6 — квадрат командами
sq8 = '''turtle.forward(150)
turtle.right(90)
turtle.forward(150)
turtle.right(90)
turtle.forward(150)
turtle.right(90)
turtle.forward(150)
turtle.right(90)'''
s = d.slide("Квадрат командами",
            "Квадрат — чотири рази «вперед і поворот на 90». Вісім рядків, і всі пари однакові. Запам’ятаймо це — "
            "за кілька слайдів скоротимо до трьох рядків.")
s.h2("Квадрат командами")
s.sub("Чотири рази: вперед — поворот.")
s.code(128, 300, 860, 560, sq8, size=30, framed=False)
s.window(1040, 300, 700, shot(t(sq8)), title="Квадрат")
with s.frame():
    s.note(900, "8 рядків — і всі пари однакові. Можна коротше?", size=34, weight=700)

# 7 — жива черепашка
s = d.slide("Жива черепашка",
            "Фізхвилинка. Викликаємо учня — він черепашка. Клас читає команди по черзі, черепашка виконує: крок — це один крок ногою. "
            "Потім питаємо: яку фігуру він «намалював»? Перша — квадрат, друга — трикутник, третя — назад на старт.", dark=True)
s.h2("Жива черепашка", size=100, top=96, width=1400)
s.sub("Хтось із класу — черепашка. Решта читає команди.", size=38)
s.code(128, 300, 520, 560, '''вперед(3)
праворуч(90)
вперед(3)
праворуч(90)
вперед(3)
праворуч(90)
вперед(3)
праворуч(90)''', size=32, framed=False)
with s.frame():
    s.code(700, 300, 520, 560, '''вперед(4)
ліворуч(120)
вперед(4)
ліворуч(120)
вперед(4)
ліворуч(120)''', size=32, framed=False)
with s.frame():
    s.code(1272, 300, 520, 330, '''вперед(5)
праворуч(180)
вперед(5)''', size=32, framed=False)
with s.frame():
    s.card(1272, 660, 520, 200, "Яку фігуру намалювали?", "Квадрат · трикутник · туди й назад", kind="darkcard",
           title_size=32, body_size=28)

# 8 — колір і товщина
col = '''turtle.pencolor("red")
turtle.pensize(8)
turtle.forward(150)
turtle.right(90)
turtle.pencolor("dodgerblue")
turtle.forward(150)
turtle.right(90)
turtle.pencolor("green")
turtle.forward(150)'''
s = d.slide("Колір і товщина",
            "pencolor — колір пензлика, назва англійською в лапках. pensize — товщина лінії. Колір можна міняти посеред малюнка: "
            "кожна наступна лінія буде вже новим кольором.")
s.h2("Колір і товщина")
s.code(128, 214, 860, 560, col, size=29, framed=False)
s.window(1040, 214, 700, shot(t(col)), title="Три кольори")
with s.frame():
    s.table(128, 810, [460, 1204], [["команда", "що робить"], ['pencolor("red")', "колір лінії — англійською"],
                                    ["pensize(8)", "товщина лінії"]], row_h=66, size=28)

# 9 — for
sqfor = '''for i in range(4):
    turtle.forward(150)
    turtle.right(90)'''
s = d.slide("Цикл for: менше рядків",
            "Згадуємо цикл з уроку 11: усе, що з відступом, повториться стільки разів, скільки в range. "
            "Вісім рядків стали трьома. А квадрат той самий.")
s.h2("Цикл for: менше рядків")
s.sub("Вісім однакових рядків → три рядки з циклом.")
s.code(128, 300, 860, 280, sqfor, size=34)
s.window(1040, 300, 700, shot(t(sqfor)), title="Той самий квадрат")
with s.frame():
    s.card(128, 620, 860, 260, "Повтори 4 рази", ["вперед на 150", "поверни на 90"], kind="blue", title_size=36, body_size=32,
           valign="flex-start")
with s.frame():
    s.note(930, "Цикл ми вже знаємо з уроку 11. Тепер він малює!", size=32)

# 10 — кроки
s = d.slide("Кроки: розмір фігури",
            "Змінюємо лише одне число — кількість кроків у forward. Фігура та сама, а розмір інший. "
            "Питаємо: що буде при forward(250)? Квадрат вилізе за край вікна — черепашка стартує з центру.")
s.h2("Кроки: розмір фігури")
s.sub("Змінюємо тільки число в " + c("forward") + ". Фігура та сама — розмір інший.")
for k, step in enumerate((40, 80, 130)):
    code = f"for i in range(4):\n    turtle.forward({step})\n    turtle.right(90)"
    with s.frame():
        x = 128 + k * 568
        s.box(x, 300, 528, 90, "screen", radius=14)
        s.text(x, 300, 528, 90, esc(f"forward({step})"), size=32, weight=700, mono=True, color=PAPER, align="center",
               valign="center")
        s.window(x, 410, 524, shot(t(code)), title=f"{step} кроків")
with s.frame():
    s.note(880, "А що буде при " + c("forward(250)") + "? Квадрат вилізе за край вікна.")

# 11 — кут
s = d.slide("Кут: яка вийде фігура",
            "Головне відкриття уроку. Щоб фігура замкнулася, черепашка має повернутися загалом на 360 градусів. "
            "Тому кут = 360 поділити на кількість сторін. 3 сторони — 120, 4 — 90, 6 — 60, 36 сторін по 10 градусів — майже коло.")
s.h2("Кут: яка вийде фігура")
s.sub("Кут = <b>360 ÷ кількість сторін</b>. Тоді фігура замкнеться.")
shapes = [(3, 160, "трикутник"), (4, 140, "квадрат"), (6, 90, "шестикутник"), (36, 16, "майже коло")]
for k, (n, side, name) in enumerate(shapes):
    with s.frame():
        x = 128 + k * 420
        s.window(x, 300, 392, shot(t(poly(n, side) .replace('turtle.pencolor("dodgerblue")', 'turtle.pencolor("dodgerblue")'))),
                 title=name)
        s.text(x, 655, 392, 50, f"range({n}) · right({round(360 / n, 2):g})", size=26, weight=700, mono=True, color=BLUE,
               align="center")
with s.frame():
    s.table(128, 740, [416, 416, 416, 416], [["сторін", "3", "4", "6"], ["кут", "120", "90", "60"]], row_h=74, size=30,
            aligns=["center"] * 4)

# 12 — зірка
s = d.slide("Зірка: магія 144",
            "П’ять разів уперед і поворот на 144 — зірка. Чому 144? Черепашка обходить коло двічі: 5 × 144 = 720 = 2 × 360. "
            "Саме тому промені перетинаються. Для дітей достатньо: «повертаємо більше, ніж для п’ятикутника».")
s.h2("Зірка: магія 144")
s.code(128, 214, 860, 330, STAR, size=32)
s.window(1040, 214, 700, shot(t(STAR)), title="Зірка")
with s.frame():
    s.card(128, 580, 860, 200, "Чому 144?", "5 × 144 = 720 — черепашка обходить коло <b>двічі</b>, тому промені перетинаються.",
           kind="orange", title_size=34, body_size=28)
with s.frame():
    s.card(128, 800, 860, 140, None, "П’ятикутник: " + c("right(72)") + " · зірка: " + c("right(144)"), kind="blue",
           body_size=30)

# 13 — сонечко
s = d.slide("Сонечко: змінимо кут ще раз",
            "36 разів уперед на 220 і поворот на 170 — майже розворот. Промені щоразу проходять трохи повз центр, і виходить сонечко. "
            "Пропонуємо учням спробувати 160, 175, 179 — кожен кут дає інший візерунок.")
s.h2("Сонечко: змінимо кут ще раз")
s.code(128, 214, 860, 380, SUN, size=32)
s.window(1040, 214, 700, shot(t(SUN, hide=True)), title="Сонечко")
with s.frame():
    s.card(128, 630, 860, 250, "Експеримент", ["Спробуйте " + c("right(160)") + ", " + c("right(175)") + ", " + c("right(179)") + ".",
                                               "Яке число дає найгарніше сонечко?"], kind="blue", title_size=34, body_size=30,
           valign="flex-start")

# 14 — вгадай фігуру
qs = [poly(3, 150, "red"), poly(8, 70, "green"), poly(5, 140, "purple").replace("right(72)", "right(144)")]
s = d.slide("Вгадай фігуру",
            "Клас голосує, потім відкриваємо справжній результат. Друга — восьмикутник: 360 ÷ 8 = 45. Третя — зірка, бо 144.")
s.h2("Вгадай фігуру")
for k, q in enumerate(qs):
    x = 128 + k * 568
    shown = "\n".join(q.split("\n")[2:])
    s.code(x, 230, 528, 200, shown, size=26, framed=False)
for k, q in enumerate(qs):
    x = 128 + k * 568
    with s.frame("pop"):
        s.window(x, 470, 524, shot(t(q)), title="Відповідь")

# 15 — типові помилки
s = d.slide("Типові помилки",
            "Перша — дуже поширена: файл назвали turtle.py, і Python підключає його замість справжньої черепашки. "
            "Друга — велика літера. Третя — кут не той, і фігура не замикається. Четверта — забули done(): вікно блимає й зникає.")
s.text(128, 420, 560, 240, "Типові<br/>помилки", size=96, weight=700, lh=1.02, extra=";letter-spacing:-3px")
with s.frame():
    s.mistake(720, 120, 1072, '''# файл назвали turtle.py
import turtle''', "Назвіть файл інакше: " + c("cherepashka.py"), code_h=110, size=26)
with s.frame():
    s.mistake(720, 360, 1072, '''turtle.Forward(100)''', "Велика літера: треба " + c("forward"), code_h=80, size=26)
with s.frame():
    s.mistake(720, 570, 1072, '''for i in range(5):
    turtle.forward(100)
    turtle.right(90)''', "5 сторін, а кут від квадрата — фігура не замкнеться: " + c("right(72)"), code_h=140, size=26)
with s.frame():
    s.mistake(720, 850, 1072, '''# забули turtle.done()''', "Вікно блимне й зникне", code_h=70, size=26)

# 16 — ваш хід
d.your_turn([("edit", "Квадрат командами, потім циклом"), ("star", "Трикутник, шестикутник, зірка"),
             ("lightning", "Сонечко: знайди найгарніший кут"), ("users", "Перша літера імені командами"),
             ("clock", "Без комп’ютера: що намалює черепашка")],
            notes="Усі завдання — без функцій і без вкладених циклів. Хто швидко впорався — наступна презентація «Черепашка-художниця».")

# 17 — завдання
s = d.task("Завдання 1–3. Фігури й кути",
           "Відповіді: трикутник range(3)/right(120), шестикутник range(6)/right(60), восьмикутник range(8)/right(45), зірка range(5)/right(144).")
s.steps(["Намалюйте квадрат <b>вісьмома командами</b>, а потім — циклом із трьох рядків.",
         "Намалюйте трикутник, шестикутник і восьмикутник. Кут рахуйте: " + c("360 ÷ сторін") + ".",
         "Кожну фігуру — іншим кольором і товщиною.",
         "Намалюйте зірку з " + c("right(144)") + ".",
         "⭐ Сонечко: змінюйте кут від 150 до 179 і знайдіть найгарніший."], w=860, size=31)
s.window(1060, 216, 700, shot(t(SUN, hide=True)), title="Сонечко — зразок")

# 18 — без комп'ютера
s = d.task("Без комп’ютера: що намалює черепашка",
           "Відповіді: а) квадрат зі стороною 100; б) трикутник; в) пряма лінія туди й назад — після right(180) черепашка йде назад по своєму сліду. "
           "Для шестикутника кут 60.", where="У зошиті")
s.steps(["Намалюйте в зошиті, що вийде в кожній програмі праворуч. Одна клітинка — 20 кроків.",
         "Позначте стрілочкою, куди дивиться черепашка наприкінці.",
         "Допишіть програму, щоб вийшов шестикутник: скільки повторів і який кут?"], w=860, size=30)
s.code(1060, 216, 732, 720, '''# а)
for i in range(4):
    turtle.forward(100)
    turtle.left(90)

# б)
for i in range(3):
    turtle.forward(120)
    turtle.left(120)

# в)
turtle.forward(100)
turtle.right(180)
turtle.forward(100)''', size=26, framed=False)

out = os.path.join(REPO, "Презентації уроків", "Python", "Урок 23. Черепашка — перші кроки.html")
print(d.save(out), len(d.slides))
