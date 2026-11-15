"""Python, урок 29. Вікно програми: напис, кнопка, поле, повзунок. Калькулятор у вікні."""
import os
from deck import Deck, c, esc, shot, shot_info, REPO, INK, INK2, ORANGE, BLUE, DARK_BG, PAPER

d = Deck("Вікно програми", kind="python", topic="Вікно програми")

HEAD = 'import tkinter\n\nвікно = tkinter.Tk()\nвікно.title("{t}")\nвікно.geometry("{g}")\nвікно.option_add("*Font", ("Arial", 20))\n\n'


def app(body, title="Моя програма", geom="400x260", extra=""):
    return extra + HEAD.format(t=title, g=geom) + body.strip() + "\n\nвікно.mainloop()\n"


EMPTY = app("", "Моя перша програма")

LABEL = '''напис = tkinter.Label(вікно, text="Привіт!", font=("Arial", 28))
напис.pack(pady=40)'''

COUNTER = '''кліків = 0

def клацнути():
    global кліків
    кліків += 1
    напис.config(text=f"Натиснуто: {кліків}")

напис = tkinter.Label(вікно, text="Натиснуто: 0")
напис.pack(pady=30)

кнопка = tkinter.Button(вікно, text="Натисни мене",
                        command=клацнути)
кнопка.pack()'''

LIGHT = '''кольори = ["red", "gold", "green"]
номер = 0

def перемкнути():
    global номер
    номер = (номер + 1) % 3
    лампа.config(bg=кольори[номер])

лампа = tkinter.Label(вікно, width=10, height=5, bg="red")
лампа.pack(pady=20)

кнопка = tkinter.Button(вікно, text="Перемкнути",
                        command=перемкнути)
кнопка.pack()'''

GREET = '''def привітати():
    текст = поле.get()
    напис.config(text=f"Привіт, {текст}!")

поле = tkinter.Entry(вікно, width=14)
поле.pack(pady=20)

кнопка = tkinter.Button(вікно, text="Привітатися",
                        command=привітати)
кнопка.pack()

напис = tkinter.Label(вікно, text="")
напис.pack(pady=20)'''

SCALE2 = '''напис = tkinter.Label(вікно, text="Скільки тобі років?")
напис.pack(pady=10)

повзунок = tkinter.Scale(вікно,
                         from_=5, to=18, orient="horizontal")
повзунок.pack()

def показати():
    вік = повзунок.get()
    відповідь.config(text=f"Через 5 років тобі буде {вік + 5}")

кнопка = tkinter.Button(вікно, text="Порахувати",
                        command=показати)
кнопка.pack(pady=10)
відповідь = tkinter.Label(вікно, text="")
відповідь.pack()'''

CALC_FN = '''def порахувати(дія):
    a = повзунок1.get()
    b = повзунок2.get()
    if дія == "+":
        результат = a + b
    elif дія == "−":
        результат = a - b
    elif дія == "×":
        результат = a * b
    else:
        if b == 0:
            messagebox.showerror("Помилка", "На нуль ділити не можна")
            return
        результат = round(a / b, 2)
    напис.config(text=f"{a} {дія} {b} = {результат}")

def плюс():
    порахувати("+")

def мінус():
    порахувати("−")

def помножити():
    порахувати("×")

def поділити():
    порахувати("÷")'''

CALC_UI = '''повзунок1 = tkinter.Scale(вікно,
                                       from_=0, to=20, orient="horizontal")
повзунок1.pack()
повзунок2 = tkinter.Scale(вікно,
                          from_=0, to=20, orient="horizontal")
повзунок2.pack()

рядок = tkinter.Frame(вікно)
рядок.pack(pady=10)
tkinter.Button(рядок, text="+", command=плюс).pack(side="left")
tkinter.Button(рядок, text="−", command=мінус).pack(side="left")
tkinter.Button(рядок, text="×", command=помножити).pack(side="left")
tkinter.Button(рядок, text="÷", command=поділити).pack(side="left")

напис = tkinter.Label(вікно, text="Оберіть числа")
напис.pack(pady=10)'''

CALC = CALC_FN + "\n\n" + CALC_UI.replace("orient=\"horizontal\")", "orient=\"horizontal\", length=360)")

MB = "from tkinter import messagebox\n"


def calc_shot(a, b, btn):
    return shot(app(CALC, "Калькулятор", "440x330", MB), [{"scale": [0, a]}, {"scale": [1, b]}, {"button": btn}])


# 1 — титул
s = d.title("Python", "Вікно програми", "Напис, кнопка, поле, повзунок",
            notes="Досі наші програми жили в консолі або на полотні. Сьогодні зробимо справжню програму з вікном, кнопками й полями — "
                  "таку, як калькулятор у телефоні. Наприкінці — калькулятор у вікні.")
s.window(1180, 150, 560, calc_shot(12, 7, 2))

# 2 — план
d.plan(["Програма з кнопками", "Порожнє вікно", "Напис: Label", "Кнопка: Button", "Лічильник кліків",
        "Кнопки-кольори", "Поле: Entry", "Повзунок: Scale", "Калькулятор у вікні", "Помилки й практика"],
       notes="Чотири нові елементи вікна: напис, кнопка, поле, повзунок. Усі вікна на слайдах — справжні скриншоти.")

# 3 — гачок
s = d.slide("Програма з кнопками",
            "Порівнюємо: консольна програма питає й чекає текст. Програма з вікном показує кнопки — і людина сама вирішує, що натиснути. "
            "Калькулятор, плеєр, налаштування телефона — усе це вікна з кнопками. Сьогодні робимо таку саму.")
s.h2("Програма з кнопками")
s.sub("Консоль питає й чекає текст. Вікно показує кнопки — і людина сама вирішує.")
s.screen(128, 330, 800, 360, ">>> \nПерше число: 12\nДруге число: 7\nДія: *\nРезультат: 84", label="КОНСОЛЬ", size=32)
with s.frame():
    s.window(992, 300, 560, calc_shot(12, 7, 2))
with s.frame():
    s.note(860, "Сьогодні — справжнє вікно: напис, кнопка, поле, повзунок.")

# 4 — порожнє вікно
s = d.slide("Порожнє вікно",
            "Майже як для полотна, але без Canvas. geometry задає розмір: ширина «x» висота — через латинську літеру x, без пробілів. "
            "option_add один раз задає шрифт для всіх написів і кнопок — тоді в кожному рядку font писати не треба. mainloop тримає вікно відкритим.")
s.h2("Порожнє вікно")
s.code(128, 214, 1000, 440, EMPTY.strip(), size=26, framed=False)
s.window(1160, 214, 560, shot(EMPTY))
with s.frame():
    s.card(128, 690, 800, 190, c('geometry("400x260")'), "ширина × висота, через латинську x, без пробілів", kind="blue",
           title_size=32, body_size=28)
with s.frame():
    s.card(960, 690, 832, 190, c("option_add(\"*Font\", …)"), "один шрифт для всіх написів і кнопок — щоб не писати його щоразу",
           kind="light", title_size=30, body_size=28)

# 5 — Label
s = d.slide("Напис: Label",
            "Label — напис у вікні. Створили — і обов’язково pack(), інакше напису не буде видно. "
            "pady — відступ зверху й знизу, щоб не тулилося до краю.")
s.h2("Напис: Label")
s.code(128, 214, 1664, 150, LABEL, size=28, framed=False)
s.window(128, 400, 560, shot(app(LABEL, "Напис")))
with s.frame():
    s.table(760, 400, [330, 702], [["параметр", "що робить"], ["text", "текст напису"], ["font", "шрифт і розмір"],
                                   ["fg / bg", "колір літер / фону"]], row_h=76, size=28)
with s.frame():
    s.card(760, 730, 1032, 160, None, "Без " + c("pack()") + " напис створений, але невидимий. " + c("pady") + " — відступ.",
           kind="orange", body_size=30)

# 6 — Button
BTN = '''def привітатися():
    напис.config(text="Кнопку натиснуто!")

напис = tkinter.Label(вікно, text="Чекаю...")
напис.pack(pady=30)

кнопка = tkinter.Button(вікно, text="Натисни мене",
                        command=привітатися)
кнопка.pack()'''
s = d.slide("Кнопка: Button",
            "Кнопка викликає функцію, указану в command. Без дужок: ми не викликаємо функцію зараз, а кажемо кнопці, кого кликати потім — "
            "так само, як у bind. config змінює вже створений напис.")
s.h2("Кнопка: Button")
s.code(128, 214, 1000, 420, BTN, size=25, framed=False)
s.window(1160, 214, 560, shot(app(BTN, "Кнопка")), title="До натискання")
with s.frame():
    s.window(1160, 600, 560, shot(app(BTN, "Кнопка"), [{"button": 0}]), title="Після натискання")
with s.frame():
    s.card(128, 670, 1000, 150, None, c("command=привітатися") + " ✅     " + c("command=привітатися()") + " ❌",
           kind="orange", body_size=32, align="center")
with s.frame():
    s.card(128, 840, 1000, 130, None, c("напис.config(text=…)") + " — змінює вже створений напис.", kind="blue",
           body_size=28)

# 6а — зроби зараз
FIRST = '''def натиснули():
    напис.config(text="Ура, працює!")

напис = tkinter.Label(вікно, text="Ще не натискали")
напис.pack(pady=30)

tkinter.Button(вікно, text="Натисни",
               command=натиснули).pack()'''
s = d.now("Зроби зараз: перша кнопка",
          "Перша віконна програма в кожного. Найчастіша помилка — дужки після імені функції в command. "
          "Хто впорався — міняє тексти й додає колір напису fg=\"blue\".", minutes=4)
s.steps(["Наберіть заготовку вікна зі слайда «Порожнє вікно».",
         "Додайте напис, кнопку і функцію з картки внизу.",
         "Запустіть і натисніть кнопку. Напис змінився?",
         "Змініть тексти на свої. ⭐ Колір напису: " + c('fg="blue"') + "."], w=860, size=31)
s.code(128, 560, 1000, 380, FIRST, size=26, framed=False)
s.window(1180, 216, 560, shot(app(FIRST, "Перша кнопка", "400x220"), [{"button": 0}]), title="Після натискання")

# 7 — лічильник
s = d.slide("Лічильник кліків",
            "Змінна кліків живе поза функцією, тому всередині пишемо global. Кожне натискання — +1 і новий текст напису. "
            "Скриншот — після шести натискань.")
s.h2("Лічильник кліків")
s.code(128, 214, 1080, 640, COUNTER, size=25, framed=False)
s.window(1240, 214, 552, shot(app(COUNTER, "Лічильник"), [{"button": 0}] * 6), title="Після 6 натискань")
with s.frame():
    s.card(1240, 640, 552, 220, c("global кліків"), "бо змінюємо змінну, створену поза функцією", kind="orange",
           title_size=30, body_size=27)

# 8 — кнопки-кольори
COLORS = '''def червоний():
    лампа.config(bg="red")

def зелений():
    лампа.config(bg="green")

лампа = tkinter.Label(вікно, width=10, height=4, bg="gray")
лампа.pack(pady=20)

tkinter.Button(вікно, text="Червоний",
               command=червоний).pack()
tkinter.Button(вікно, text="Зелений",
               command=зелений).pack()'''
s = d.slide("Кнопки-кольори",
            "Кожна кнопка — своя маленька функція. Жодних лічильників і global: функція просто перефарбовує лампу через config. "
            "Label без тексту, але з шириною й висотою — це кольоровий прямокутник. Питаємо: як додати жовтий?")
s.h2("Кнопки-кольори")
s.sub("Одна кнопка — одна функція.")
s.code(128, 300, 1000, 600, COLORS, size=24, framed=False)
for k, n in enumerate((0, 1)):
    with s.frame():
        s.window(1160 + k * 320, 300, 300, shot(app(COLORS, "Лампа", "300x300"), [{"button": n}]),
                 title="Червоний" if n == 0 else "Зелений")
with s.frame():
    s.card(1160, 680, 632, 220, "А жовтий?", "Ще одна функція з " + c('bg="gold"') + " і ще одна кнопка.", kind="blue",
           title_size=32, body_size=28)

# 9 — Entry
s = d.slide("Поле: Entry",
            "Entry — поле, куди людина пише текст. get() забирає написане. Тут текст лишається текстом, тож нічого перетворювати не треба. "
            "Скриншот — після того, як у поле написали «Оля» й натиснули кнопку.")
s.h2("Поле: Entry")
s.code(128, 214, 1000, 640, GREET, size=25, framed=False)
s.window(1160, 214, 560, shot(app(GREET, "Привітання", "400x280"), [{"type": [0, "Оля"]}, {"button": 0}]))
with s.frame():
    s.card(1160, 640, 632, 220, c("поле.get()"), "забирає те, що людина написала в полі — завжди текстом", kind="blue",
           title_size=30, body_size=27)

# 10 — Scale
s = d.slide("Повзунок: Scale",
            "Повзунок — найзручніший спосіб отримати число: людина тягне бігунець, а get() одразу повертає ціле число. "
            "Ні тексту, ні перетворень. from_ з підкресленням, бо from у Python зайняте слово.")
s.h2("Повзунок: Scale")
s.sub("Людина тягне бігунець — а " + c("get()") + " одразу повертає <b>число</b>.")
s.code(128, 300, 1080, 640, SCALE2, size=23, framed=False)
s.window(1240, 300, 552, shot(app(SCALE2, "Повзунок", "420x280"), [{"scale": [0, 12]}, {"button": 0}]))
with s.frame():
    s.card(1240, 720, 552, 200, "Чому from_?", c("from") + " у Python — зайняте слово, тому з підкресленням.", kind="orange",
           title_size=30, body_size=27)

# 11 — калькулятор: вікно
s = d.slide("Калькулятор: вікно",
            "Спершу збираємо вікно: два повзунки, рядок із чотирьох кнопок (Frame — невидима коробка, щоб кнопки стали в ряд, "
            "side=\"left\" — одна за одною) і напис для результату. Кожна кнопка кличе свою маленьку функцію.")
s.h2("Калькулятор: вікно")
s.code(128, 214, 1080, 640, CALC_UI, size=24, framed=False)
s.window(1240, 214, 552, calc_shot(12, 7, 0), title="12 + 7")
with s.frame():
    s.card(1240, 680, 552, 200, c("Frame"), "невидима коробка: кнопки в ній стають у ряд через " + c('side="left"'),
           kind="blue", title_size=30, body_size=26)

# 12 — калькулятор: функції
PLUS = '''def плюс():
    a = повзунок1.get()
    b = повзунок2.get()
    напис.config(text=f"{a} + {b} = {a + b}")

def помножити():
    a = повзунок1.get()
    b = повзунок2.get()
    напис.config(text=f"{a} × {b} = {a * b}")'''
s = d.slide("Калькулятор: функції",
            "Кожна кнопка — своя функція з трьох рядків: взяти два числа з повзунків, порахувати, показати в написі. "
            "get() у повзунка одразу дає число — нічого перетворювати не треба. Мінус і ділення пишуться так само. "
            "Для сильних: одна велика функція порахувати(дія) на всі кнопки — рівень 3 практики.")
s.h2("Калькулятор: функції")
s.sub("Взяти два числа — порахувати — показати. Три рядки на кнопку.")
s.code(128, 300, 1080, 600, PLUS, size=25, framed=False)
with s.frame():
    s.window(1240, 300, 552, calc_shot(12, 7, 2), title="12 × 7")
with s.frame():
    s.card(1240, 790, 552, 170, "Мінус і ділення", "Так само — лише інший знак у двох місцях.", kind="blue",
           title_size=30, body_size=27)

# 12 — messagebox
mb_png = calc_shot(9, 0, 3)
kind, ttl, msg = shot_info(mb_png)[4].split("|")
s = d.slide("⭐ messagebox: вікно-попередження",
            "Ділити на нуль не можна. Замість того щоб програма впала з помилкою, показуємо вікно-попередження й виходимо з функції через return. "
            "Три види: showinfo, showwarning, showerror.")
s.h2("⭐ messagebox: вікно-попередження")
s.code(128, 214, 1000, 260, '''from tkinter import messagebox

if b == 0:
    messagebox.showerror("Помилка", "На нуль ділити не можна")
    return''', size=26, framed=False)
s.window(128, 510, 560, mb_png, title="9 ÷ 0")
with s.frame():
    s.raw(f'<div style="position:absolute;left:520px;top:620px;width:520px;height:250px;background:#F4F6F9;'
          f'border:2px solid {DARK_BG};border-radius:14px;box-shadow:0 20px 50px rgba(20,30,50,0.35)">'
          f'<div style="height:46px;border-bottom:2px solid {DARK_BG};display:flex;align-items:center;padding:0 18px">'
          f'<p style="font-size:22px;font-weight:700;color:{INK}">{esc(ttl)}</p></div>'
          f'<div style="display:flex;flex-direction:row;align-items:center;gap:20px;padding:28px 24px">'
          f'<div style="width:56px;height:56px;border-radius:50%;background:#D9534F;display:flex;align-items:center;'
          f'justify-content:center"><p style="font-size:36px;font-weight:800;color:#fff">!</p></div>'
          f'<p style="font-size:26px;color:{INK}">{esc(msg)}</p></div>'
          f'<div style="position:absolute;right:24px;bottom:20px;width:110px;height:44px;border:2px solid {DARK_BG};'
          f'border-radius:8px;display:flex;align-items:center;justify-content:center;background:#fff">'
          f'<p style="font-size:22px;color:{INK}">OK</p></div></div>')
with s.frame():
    s.table(1160, 510, [330, 302], [["команда", "значок"], ["showinfo", "ℹ️ інформація"], ["showwarning", "⚠️ увага"],
                                    ["showerror", "⛔ помилка"]], row_h=76, size=28)
with s.frame():
    s.card(1160, 840, 632, 140, None, c("return") + " — вийти з функції, нічого не рахуючи.", kind="blue", body_size=28)

# 13 — типові помилки
s = d.slide("Типові помилки",
            "Перша — дужки в command: функція спрацює один раз при запуску, а кнопка потім нічого не робить. "
            "Друга — забули pack: елемента не видно. Третя — itemconfig замість config: itemconfig — для фігур на полотні. "
            "Четверта — забули global.")
s.text(128, 420, 560, 240, "Типові<br/>помилки", size=96, weight=700, lh=1.02, extra=";letter-spacing:-3px")
with s.frame():
    s.mistake(720, 120, 1072, '''tkinter.Button(вікно, text="OK", command=привітатися())''',
              "Дужки: функція спрацює при запуску, а кнопка — ні", code_h=80, size=24)
with s.frame():
    s.mistake(720, 330, 1072, '''напис = tkinter.Label(вікно, text="Привіт")
# забули напис.pack()''', "Без " + c("pack()") + " напису не видно", code_h=110, size=24)
with s.frame():
    s.mistake(720, 570, 1072, '''напис.itemconfig(text="Готово")''',
              "Для вікна — " + c("config") + ", " + c("itemconfig") + " — для полотна", code_h=80, size=24)
with s.frame():
    s.mistake(720, 780, 1072, '''def клацнути():
    кліків += 1        # UnboundLocalError''', "Забули " + c("global кліків"), code_h=110, size=24)

PREDICT = '''передбачення = ["Сьогодні тобі пощастить!",
                "Чекай на дванадцятку",
                "Тебе чекає сюрприз",
                "Час на перерву"]

def передбачити():
    напис.config(text=random.choice(передбачення))

tkinter.Button(вікно, text="Що мене чекає?",
               command=передбачити).pack(pady=30)

напис = tkinter.Label(вікно, text="Натисни кнопку",
                      fg="purple")
напис.pack()'''
CALC_GAPS = '''def плюс():
    a = повзунок1.get()
    b = повзунок2.get()
    напис.config(text=f"{a} + {b} = {a + b}")

def мінус():
    a = повзунок1.get()
    b = ___
    напис.config(text=f"{a} − {b} = {___}")'''

# 14 — ваш хід
d.your_turn([("star", "Рівень 1: кнопка-передбачення"), ("edit", "Рівень 2: допиши калькулятор"),
             ("lightning", "Рівень 3: повний калькулятор"), ("clock", "Без комп’ютера: проєкт вікна на папері")],
            notes="Рівень 1 — готова весела програма, учні змінюють тексти й кольори. Рівень 2 — дописати мінус, множення й ділення "
                  "за зразком плюса. Рівень 3 — калькулятор з однією функцією, захистом від нуля й кнопкою «Очистити».")

# 14а — рівні
d.levels([("Передбачення", "готовий код", ["Свої передбачення у списку.", "Інші кольори й тексти.",
                                           "⭐ Друга кнопка «Комплімент»."]),
          ("Допиши", "калькулятор за зразком", ["Мінус, множення, ділення — як плюс.", "Чотири кнопки в ряд."]),
          ("Вигадай", "повний калькулятор", ["Ділення на нуль — " + c("messagebox") + ".", "Кнопка «Очистити».",
                                             "Одна функція " + c("порахувати(дія)") + "."])],
         notes="Рівень 1 — під силу кожному.")

# 15 — рівень 1
s = d.task("Рівень 1. Кнопка-передбачення",
           "Не забути import random на початку. Друга кнопка — ще одна функція зі своїм списком компліментів. "
           "Можна зробити кнопку-кубик: random.randint(1, 6).")
s.code(128, 216, 1000, 760, PREDICT, size=25, framed=False)
s.steps(["Додайте " + c("import random") + " і запустіть готовий код.",
         "Допишіть у список свої передбачення.",
         "Змініть колір напису й текст кнопки.",
         "⭐ Друга кнопка «Комплімент» зі своїм списком."], x=1180, y=630, w=612, size=29)
s.window(1180, 216, 600, shot(app(PREDICT, "Передбачення", "460x240", "import random\nrandom.seed(2)\n"), [{"button": 0}]),
         title="Після натискання")

# 15а — рівень 2
s = d.task("Рівень 2. Допиши калькулятор",
           "Пропуски: b = повзунок2.get() і a - b. Множення й ділення — так само; ділення можна округлити round(a / b, 2). "
           "Кнопки — з command=мінус без дужок.")
s.code(128, 216, 1000, 480, CALC_GAPS, size=25, framed=False)
s.steps(["Візьміть вікно калькулятора зі слайда «Калькулятор: вікно».",
         "Заповніть пропуски " + c("___") + " у функції " + c("мінус") + ".",
         "За тим самим зразком напишіть " + c("помножити") + " і " + c("поділити") + ".",
         "Перевірте кожну кнопку: 12 і 4 → 16, 8, 48, 3."], x=128, y=730, w=1000, size=29)
s.window(1180, 216, 560, calc_shot(12, 4, 1), title="12 − 4")

# 15б — рівень 3
s = d.task("Рівень 3. Повний калькулятор",
           "Критерії: два повзунки, чотири дії, напис-результат, захист від ділення на нуль через messagebox, "
           "одна функція порахувати(дія) замість чотирьох схожих, кнопка «Очистити».", where="Для сильних")
s.steps(["Одна функція " + c("порахувати(дія)") + " з " + c("if / elif") + " на всі кнопки; кнопка кличе її зі своїм знаком.",
         "Ділення на нуль — вікно " + c("messagebox.showerror") + " і " + c("return") + ".",
         "Кнопка «Очистити»: повзунки на 0 через " + c("повзунок1.set(0)") + ", напис — порожній.",
         "⭐ Кнопка " + c("xʸ") + " для степеня."], w=860, size=31)
s.window(1060, 216, 620, calc_shot(12, 7, 2), title="Зразок")

# 16 — без комп'ютера
s = d.task("Без комп’ютера: проєкт вікна на папері",
           "Зараховуємо, якщо: намальовано вікно з усіма елементами, біля кожного підписано тип (Label, Button, Entry, Scale), "
           "для кожної кнопки названо функцію-обробник і що вона змінює.", where="У зошиті")
s.steps(["Намалюйте вікно програми «Конвертер гривень у долари»: повзунок, кнопка, напис-результат.",
         "Біля кожного елемента підпишіть: " + c("Label") + ", " + c("Button") + ", " + c("Scale") + ".",
         "Запишіть функцію, яку викличе кнопка, і що вона змінить.",
         "Знайдіть помилку: " + c('tkinter.Button(вікно, text="OK", command=рахувати())') + "."], w=1100, size=30)

out = os.path.join(REPO, "Презентації уроків", "Python", "Урок 29. Вікно програми.html")
print(d.save(out), len(d.slides))
