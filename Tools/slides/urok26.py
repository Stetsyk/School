"""Python, урок 26. Хатинка з фігур. Проєкт «Вулиця»."""
import os
from deck import Deck, c, esc, shot, REPO, INK, INK2, ORANGE, BLUE, DARK_BG, PAPER
from grafika import prog

d = Deck("Хатинка й вулиця", kind="python", topic="Хатинка й вулиця")


def at(o, cx, cy):
    ox, oy, k = o
    return ox + (cx + 1) * k, oy + (cy + 1) * k


HOUSE_FN = '''def хатинка(x, y, колір):
    полотно.create_rectangle(x, y, x + 100, y + 80, fill=колір)
    полотно.create_polygon(x - 10, y, x + 50, y - 50, x + 110, y,
                           fill="brown")
    полотно.create_rectangle(x + 40, y + 40, x + 60, y + 80,
                             fill="saddlebrown")
    полотно.create_rectangle(x + 10, y + 15, x + 30, y + 35,
                             fill="lightblue")'''

TREE_FN = '''def дерево(x, y):
    полотно.create_rectangle(x - 6, y - 40, x + 6, y,
                             fill="sienna")
    полотно.create_oval(x - 30, y - 100, x + 30, y - 30,
                        fill="forestgreen")'''

STREET = f'''import random

{HOUSE_FN}

{TREE_FN}

полотно.create_rectangle(0, 0, 600, 280, fill="skyblue", outline="")
полотно.create_oval(480, 30, 560, 110, fill="gold", outline="")
полотно.create_rectangle(0, 280, 600, 400, fill="lightgreen", outline="")

кольори = ["lightyellow", "pink", "lightblue", "wheat", "lavender"]
random.seed(4)
for i in range(4):
    хатинка(30 + i * 145, 230, random.choice(кольори))
for i in range(5):
    дерево(15 + i * 145, 380)

полотно.create_text(300, 385, text="Вулиця Сонячна", font=("Arial", 14))'''

# 1 — титул
s = d.title("Python", "Хатинка й вулиця", "Функції та цикли на полотні",
            notes="Сьогодні з простих фігур збираємо хатинку, загортаємо її у функцію — і одним циклом будуємо цілу вулицю. "
                  "Наприкінці уроку кожен намалює свою вулицю, не схожу на сусідську.")
s.window(1180, 150, 600, shot(prog(STREET, title="Вулиця")))

# 2 — план
d.plan(["Хатинка — це п’ять фігур", "Трикутник: create_polygon", "Спершу креслення", "Хатинка кодом",
        "А якщо треба п’ять?", "Хатинка у функції", "Цикл будує вулицю", "Різні кольори з random",
        "Фон і друга функція", "Помилки й проєкт «Вулиця»"],
       notes="Головна ідея уроку: описати хатинку один раз — і ставити скільки завгодно.")

# 3 — гачок
parts = '''полотно.create_rectangle(200, 180, 400, 340, fill="lightyellow", width=2)
полотно.create_polygon(180, 180, 300, 80, 420, 180, fill="brown", width=2, outline="black")
полотно.create_rectangle(280, 260, 320, 340, fill="saddlebrown")
полотно.create_rectangle(220, 210, 260, 250, fill="lightblue")
полотно.create_rectangle(340, 210, 380, 250, fill="lightblue")
полотно.create_rectangle(350, 90, 375, 150, fill="gray")'''
s = d.slide("Хатинка — це п’ять фігур",
            "Подивіться на дитячий малюнок будинку: квадрат — стіни, трикутник — дах, квадратики — вікна, прямокутник — двері, "
            "вузький прямокутник — комин. Усе це вже вміємо, крім трикутника. Його навчимося зараз.")
s.h2("Хатинка — це п’ять фігур")
s.sub("Стіни, дах, двері, вікна, комин. Усі, крім даху, — прямокутники.")
s.window(128, 300, 860, shot(prog(parts, title="Хатинка")))
names = [("Стіни", "прямокутник", "light"), ("Дах", "трикутник — новий!", "orange"), ("Двері", "прямокутник", "light"),
         ("Вікна", "два квадрати", "light"), ("Комин", "вузький прямокутник", "light")]
for k, (n, f, kind) in enumerate(names):
    with s.frame():
        s.card(1040, 300 + k * 128, 752, 108, None, f"<b>{n}</b> — {f}", kind=kind, body_size=32)

# 4 — polygon
tri = 'полотно.create_polygon(100, 300, 300, 80, 500, 300, fill="brown", outline="black", width=3)'
s = d.slide("Трикутник: create_polygon",
            "create_polygon з’єднує точки по черзі й замикає фігуру — остання точка з’єднується з першою. "
            "Три точки — трикутник, чотири — чотирикутник, скільки завгодно — будь-який багатокутник. "
            "Без outline контуру не буде — лише заливка.")
s.h2("Трикутник: create_polygon")
s.code(128, 214, 1664, 120, tri, size=26, framed=False)
o = s.window(128, 370, 860, shot(prog(tri, title="Трикутник")))
for i, (x, y, side) in enumerate([(100, 300, "left"), (300, 80, "right"), (500, 300, "right")]):
    with s.frame():
        s.marker(*at(o, x, y), f"({x}, {y})", side=side)
with s.frame():
    s.card(1040, 370, 752, 230, "Точки по черзі", "Остання точка сама з’єднується з першою — фігура замкнена.",
           kind="blue", title_size=34, body_size=29)
with s.frame():
    s.card(1040, 630, 752, 230, "Не тільки трикутник", "4 точки — ромб, 5 — п’ятикутник, 10 — зірка.", kind="light",
           title_size=34, body_size=29)

# 5 — креслення
s = d.slide("Спершу креслення, потім код",
            "Найкорисніша звичка уроку: спершу намалювати хатинку на клітинках і підписати координати кутів. "
            "Код пишеться потім за хвилину, і в ньому не буде помилок. Одна клітинка тут — 20 точок.")
s.h2("Спершу креслення, потім код")
gx, gy, cell = 128, 230, 30
cols, rows = 20, 14
s.raw(f'<div style="position:absolute;left:{gx}px;top:{gy}px;width:{cols * cell}px;height:{rows * cell}px;background:#fff;'
      f'border:2px solid {DARK_BG};background-image:linear-gradient(#E3E8EE 2px,transparent 2px),'
      f'linear-gradient(90deg,#E3E8EE 2px,transparent 2px);background-size:{cell}px {cell}px"></div>')
k = cell / 20  # клітинка = 20 точок полотна


def P(x, y):
    return gx + x * k, gy + y * k


# хатинка на кресленні: x=100, y=150
pts_wall = [P(100, 150), P(300, 150), P(300, 270), P(100, 270)]
s.raw(f'<svg style="position:absolute;left:0px;top:0px" width="1920" height="1080" viewBox="0 0 1920 1080">'
      f'<rect x="{P(100, 150)[0]}" y="{P(100, 150)[1]}" width="{200 * k}" height="{120 * k}" fill="none" stroke="{INK}" stroke-width="4"/>'
      f'<polygon points="{P(80, 150)[0]},{P(80, 150)[1]} {P(200, 50)[0]},{P(200, 50)[1]} {P(320, 150)[0]},{P(320, 150)[1]}" '
      f'fill="none" stroke="{ORANGE}" stroke-width="4"/>'
      f'<rect x="{P(180, 200)[0]}" y="{P(180, 200)[1]}" width="{40 * k}" height="{70 * k}" fill="none" stroke="{BLUE}" stroke-width="4"/></svg>')
labels = [(300, 270, "(300, 270)", "right"), (200, 50, "(200, 50)", "right"),
          (80, 150, "(80, 150)", "left"), (320, 150, "(320, 150)", "right")]
for x, y, t, side in labels:
    with s.frame():
        s.marker(*P(x, y), t, color=ORANGE if y in (50,) or x in (80, 320) else BLUE, side=side)
with s.frame():
    s.code(900, 230, 892, 360, '''# стіни
create_rectangle(100, 150, 300, 270)
# дах
create_polygon(80, 150, 200, 50, 320, 150)
# двері
create_rectangle(180, 200, 220, 270)''', size=26, framed=False)
with s.frame():
    s.card(900, 620, 892, 210, "Клітинка = 20 точок",
           "Кути фігур — на перетинах ліній. Підписали — і код майже готовий.", kind="blue", title_size=32, body_size=28)

# 6 — хатинка кодом
house_abs = '''полотно.create_rectangle(100, 150, 300, 270, fill="lightyellow")
полотно.create_polygon(80, 150, 200, 50, 320, 150, fill="brown")
полотно.create_rectangle(180, 200, 220, 270, fill="saddlebrown")
полотно.create_rectangle(120, 170, 160, 210, fill="lightblue")
полотно.create_rectangle(240, 170, 280, 210, fill="lightblue")'''
s = d.slide("Хатинка кодом",
            "П’ять рядків — і хатинка готова. Перевіряємо за кресленням: усі числа звідти. "
            "Порядок важливий: стіни спершу, вікна й двері потім — інакше стіни їх закриють.")
s.h2("Хатинка кодом")
s.code(128, 214, 1664, 280, house_abs, size=26, framed=False)
s.window(128, 530, 700, shot(prog(house_abs, title="Хатинка")))
with s.frame():
    s.card(880, 530, 912, 200, "Порядок має значення", "Спершу стіни, потім вікна й двері — інакше стіни їх закриють.",
           kind="orange", title_size=32, body_size=28)
with s.frame():
    s.card(880, 760, 912, 200, "А якщо потрібна друга хатинка?",
           "Доведеться перерахувати всі 22 числа. А для п’яти хатинок — 110.", kind="light", title_size=32, body_size=28)

# 7 — функція
s = d.slide("Хатинка у функції",
            "Головний прийом. Замість чисел — x і y лівого верхнього кута стін, а всі інші точки рахуємо від них: x + 100, y + 80. "
            "Тепер хатинку можна поставити будь-де одним рядком. Функції ми вже вміємо з уроків 20–21.")
s.h2("Хатинка у функції")
s.sub("Усі координати рахуємо від однієї точки " + c("(x, y)") + " — лівого верхнього кута стін.")
s.code(128, 300, 1100, 470, HOUSE_FN, size=25, framed=False)
call = HOUSE_FN + '\n\nхатинка(100, 200, "lightyellow")\nхатинка(330, 160, "pink")'
with s.frame():
    o = s.window(1260, 300, 532, shot(prog(call, title="Дві хатинки")))
with s.frame():
    s.code(1260, 720, 532, 150, 'хатинка(100, 200, "lightyellow")\nхатинка(330, 160, "pink")', size=22, framed=False)
with s.frame():
    s.note(910, "Один рядок — одна хатинка. Змінюємо " + c("x") + " і " + c("y") + " — хатинка переїжджає.")

# 8 — як рахуються точки
s = d.slide("Звідки x + 100 і y − 50?",
            "Розбираємо, як абсолютні числа стають відносними. Стіни шириною 100 і висотою 80: правий кут — x + 100, низ — y + 80. "
            "Вершина даху на 50 вище й посередині: x + 50, y − 50. Якщо зрозуміти це, можна намалювати будь-що.")
s.h2("Звідки x + 100 і y − 50?")
o = s.window(128, 230, 760, shot(prog(HOUSE_FN + '\n\nхатинка(220, 170, "lightyellow")', title="Хатинка")))
ref = [(220, 170, "(x, y)", "left", BLUE), (320, 250, "(x+100, y+80)", "right", BLUE), (270, 120, "(x+50, y−50)", "right", ORANGE)]
for x, y, t, side, col in ref:
    with s.frame():
        s.marker(*at(o, x, y), t, color=col, side=side)
with s.frame():
    s.table(940, 230, [380, 470], [["точка", "координати"], ["лівий верх стін", "x, y"], ["правий низ стін", "x + 100, y + 80"],
                                   ["вершина даху", "x + 50, y − 50"], ["кути даху", "x − 10 і x + 110"]], row_h=84, size=30)
with s.frame():
    s.card(940, 690, 852, 200, None, "x і y — це «якір». Решта точок не мають власних чисел — лише відстань від якоря.",
           kind="blue", body_size=30)

# 9 — цикл
row = HOUSE_FN + '\n\nfor i in range(5):\n    хатинка(20 + i * 120, 200, "lightyellow")'
s = d.slide("Цикл будує вулицю",
            "Тепер магія: цикл ставить п’ять хатинок. Кожна наступна на 120 точок правіше. Змінна i — номер хатинки: 0, 1, 2, 3, 4. "
            "Питаємо: що змінити, щоб хатинок було шість? Щоб вони стояли щільніше?")
s.h2("Цикл будує вулицю")
s.code(128, 214, 1664, 150, 'for i in range(5):\n    хатинка(20 + i * 120, 200, "lightyellow")', size=30, framed=False)
s.window(128, 400, 800, shot(prog(row, title="Вулиця")))
with s.frame():
    s.table(1180, 400, [180, 432], [["i", "x хатинки"]] + [[str(i), f"20 + {i} · 120 = {20 + i * 120}"] for i in range(5)],
            row_h=72, size=28)
with s.frame():
    s.card(1180, 860, 612, 120, None, "Шість хатинок? " + c("range(6)") + " і крок менший.", kind="blue", body_size=28)

# 10 — random кольори
rnd = 'import random\n\n' + HOUSE_FN + '''

кольори = ["lightyellow", "pink", "lightblue", "wheat", "lavender"]
for i in range(5):
    хатинка(20 + i * 120, 200, random.choice(кольори))'''
s = d.slide("Різні кольори з random",
            "Однакові хатинки — нудно. random.choice бере випадковий колір зі списку, і щоразу вулиця інша. "
            "Три запуски — три різні вулиці. Можна так само випадково міняти висоту чи відступ.")
s.h2("Різні кольори з random")
s.code(128, 214, 1664, 190, '''кольори = ["lightyellow", "pink", "lightblue", "wheat", "lavender"]
for i in range(5):
    хатинка(20 + i * 120, 200, random.choice(кольори))''', size=26, framed=False)
for k, seed in enumerate([1, 7, 23]):
    code = rnd.replace("кольори = [", f"random.seed({seed})\nкольори = [")
    with s.frame():
        s.window(128 + k * 568, 450, 528, shot(prog(code, title=f"Запуск {k + 1}")))
with s.frame():
    s.note(880, "Той самий код — щоразу нова вулиця.")

# 11 — фон і друга функція
s = d.slide("Фон і друга функція",
            "Справжня вулиця: небо, сонце, трава й дерева. Фон малюємо першим, бо все, що пізніше, лягає зверху. "
            "Дерево — друга власна функція: стовбур і крона. Це і є проєкт «Вулиця».")
s.h2("Фон і друга функція")
s.code(128, 214, 860, 360, TREE_FN, size=24, framed=False)
with s.frame():
    s.code(128, 600, 860, 300, '''# фон — першим!
полотно.create_rectangle(0, 0, 600, 280, fill="skyblue")
полотно.create_rectangle(0, 280, 600, 400, fill="lightgreen")
полотно.create_oval(480, 30, 560, 110, fill="gold")''', size=24, framed=False)
with s.frame():
    s.window(1020, 214, 772, shot(prog(STREET, title="Вулиця Сонячна")))
with s.frame():
    s.card(1020, 780, 772, 140, None, "Фон першим, будинки й дерева — поверх.", kind="blue", body_size=30)

# 12 — що зміниться
s = d.slide("Що зміниться?",
            "Змінюємо одне число — клас передбачає результат. Перше: крок 120 → 60, хатинки налізуть одна на одну. "
            "Друге: y = 50 — хатинки злетять угору, дахи вийдуть за край. Третє: range(3) — лише три.")
s.h2("Що зміниться?")
variants = [("хатинка(20 + i * 60, 200, …)", HOUSE_FN + '\n\nfor i in range(5):\n    хатинка(20 + i * 60, 200, "lightyellow")'),
            ("хатинка(20 + i * 120, 30, …)", HOUSE_FN + '\n\nfor i in range(5):\n    хатинка(20 + i * 120, 30, "lightyellow")'),
            ("for i in range(3):", HOUSE_FN + '\n\nfor i in range(3):\n    хатинка(20 + i * 120, 200, "lightyellow")')]
for k, (lbl, code) in enumerate(variants):
    x = 128 + k * 568
    s.box(x, 230, 528, 110, "screen")
    s.text(x, 230, 528, 110, esc(lbl), size=24, mono=True, color=PAPER, align="center", valign="center")
for k, (lbl, code) in enumerate(variants):
    x = 128 + k * 568
    with s.frame("pop"):
        s.window(x, 380, 524, shot(prog(code)), title="Результат")

# 13 — типові помилки
s = d.slide("Типові помилки",
            "Перша — найчастіша: у функції лишились числа замість x + …, тому всі хатинки малюються в одному місці. "
            "Друга — фон намальовано після хатинок і він їх закрив. Третя — у polygon непарна кількість чисел.")
s.text(128, 200, 560, 240, "Типові<br/>помилки", size=96, weight=700, lh=1.02, extra=";letter-spacing:-3px")
bad1 = '''def хатинка(x, y, колір):
    полотно.create_rectangle(100, 150, 200, 230, fill=колір)

for i in range(5):
    хатинка(20 + i * 120, 200, "pink")'''
with s.frame():
    s.mistake(720, 130, 1072, '''def хатинка(x, y, колір):
    полотно.create_rectangle(100, 150, 200, 230, …)''',
              "Числа замість " + c("x + …") + ": усі п’ять хатинок в одному місці", code_h=110, size=24)
with s.frame():
    s.mistake(720, 390, 1072, '''хатинка(100, 200, "pink")
полотно.create_rectangle(0, 0, 600, 400, fill="skyblue")''',
              "Фон після хатинки — і він її закрив", code_h=110, size=24)
with s.frame():
    s.mistake(720, 650, 1072, '''полотно.create_polygon(80, 150, 200, 50, 320)''',
              "Непарна кількість чисел: кожна точка — це пара x, y", code_h=80, size=24)
s.window(128, 560, 520, shot(prog(bad1, title="Де п’ять хатинок?")))

# 14 — ваш хід
d.your_turn([("home", "Хатинка за кресленням"), ("wrench", "Функція хатинка(x, y, колір)"),
             ("reload", "Вулиця з п’яти хатинок циклом"), ("star", "Проєкт «Вулиця»"),
             ("clock", "Без комп’ютера: креслення на клітинках")],
            notes="Перші три завдання — кроки до проєкту. Проєкт «Вулиця» оцінюється: критерії на наступному слайді.")

# 15 — проєкт
s = d.task("Проєкт «Вулиця»",
           "Критерії: п’ять і більше хатинок циклом (3 бали), друга власна функція (2), фон (2), random (2), підпис (1), "
           "охайність і власна ідея (2). Разом 12.")
s.steps(["П’ять і більше хатинок, розставлених <b>циклом</b>.",
         "Друга власна функція: дерево, ліхтар, хмара, паркан.",
         "Фон: небо, трава, сонце — намальовані <b>першими</b>.",
         "Випадкові кольори або розміри через " + c("random") + ".",
         "Назва вулиці й підпис автора через " + c("create_text") + "."], w=860, size=31)
s.window(1060, 216, 732, shot(prog(STREET, title="Вулиця Сонячна")), title="Зразок проєкту")
s.table(1060, 790, [520, 208], [["Що оцінюємо", "балів"], ["хатинки циклом + функція-друга", "5"],
                                ["фон, random, підпис", "5"], ["охайність і власна ідея", "2"]], row_h=50, size=22)

# 16 — без комп'ютера
s = d.task("Без комп’ютера: креслення на клітинках",
           "Відповіді: вершина даху — (x + 50, y − 50). Для хатинки з x = 200, y = 100: стіни (200, 100)–(300, 180), "
           "дах (190, 100), (250, 50), (310, 100).", where="У зошиті")
s.steps(["Накресліть полотно на клітинках, клітинка — 20 точок.",
         "Намалюйте хатинку з якорем у точці (200, 100) і підпишіть координати всіх кутів.",
         "Запишіть виклик функції, що ставить таку хатинку.",
         "Запишіть цикл, який ставить 4 хатинки з кроком 130."], w=1000, size=30)

out = os.path.join(REPO, "Презентації уроків", "Python", "Урок 26. Хатинка й вулиця.html")
print(d.save(out), len(d.slides))
