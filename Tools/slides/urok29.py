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
        "Світлофор на кнопці", "Поле: Entry", "Повзунок: Scale", "Калькулятор у вікні", "messagebox і помилки"],
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

# 8 — світлофор
s = d.slide("Світлофор на кнопці",
            "Список кольорів і номер поточного. Кожне натискання — номер + 1, а остача від ділення на 3 повертає його на 0 після 2. "
            "Label без тексту, але з шириною й висотою — просто кольоровий прямокутник.")
s.h2("Світлофор на кнопці")
s.code(128, 214, 1000, 640, LIGHT, size=25, framed=False)
for k, n in enumerate((0, 1, 2)):
    with s.frame():
        s.window(1160 + k * 214, 214, 200, shot(app(LIGHT, "Світлофор", "260x260"), [{"button": 0}] * n), title=f"{n} клік")
with s.frame():
    s.card(1160, 500, 632, 220, c("(номер + 1) % 3"), "0 → 1 → 2 → 0 → 1 … — по колу, як у шифрі Цезаря", kind="blue",
           title_size=30, body_size=27)

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
s = d.slide("Калькулятор: функції",
            "Одна велика функція порахувати(дія) — ланцюжок elif, як на уроці 8. І чотири маленькі функції для кнопок: "
            "кожна просто кличе велику зі своїм знаком. Числа беремо з повзунків — get() одразу дає число.")
s.h2("Калькулятор: функції")
s.code(128, 214, 1080, 860, CALC_FN, size=22, lh=1.34, framed=False)
with s.frame():
    s.window(1240, 214, 552, calc_shot(15, 4, 3), title="15 ÷ 4")
with s.frame():
    s.card(1240, 640, 552, 250, "Велика й маленькі",
           c("порахувати(дія)") + " рахує, а " + c("плюс()") + ", " + c("мінус()") + "… лише кажуть, яку дію взяти.",
           kind="blue", title_size=30, body_size=26)

# 12 — messagebox
mb_png = calc_shot(9, 0, 3)
kind, ttl, msg = shot_info(mb_png)[4].split("|")
s = d.slide("messagebox: вікно-попередження",
            "Ділити на нуль не можна. Замість того щоб програма впала з помилкою, показуємо вікно-попередження й виходимо з функції через return. "
            "Три види: showinfo, showwarning, showerror.")
s.h2("messagebox: вікно-попередження")
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

# 14 — ваш хід
d.your_turn([("play", "Лічильник кліків із кнопкою «Скинути»"), ("lightning", "Світлофор на кнопці"),
             ("users", "Привітання з полем"), ("star", "Калькулятор на повзунках"),
             ("clock", "Без комп’ютера: проєкт вікна на папері")],
            notes="Три розминки й головне завдання — калькулятор. Хто швидко впорався — додає кнопку «Очистити» "
                  "або піднесення до степеня.")

# 15 — завдання
s = d.task("Завдання. Калькулятор у вікні",
           "Критерії: два повзунки, чотири дії, напис-результат, захист від ділення на нуль через messagebox, функції замість повторів.")
s.steps(["Два повзунки від 0 до 20.",
         "Чотири кнопки: +, −, ×, ÷. Одна функція " + c("порахувати(дія)") + " на всі.",
         "Напис показує весь приклад: " + c("12 × 7 = 84") + ".",
         "Ділення на нуль — вікно " + c("messagebox.showerror") + ".",
         "⭐ Кнопка «Очистити» і кнопка " + c("xʸ") + " для степеня."], w=860, size=31)
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
