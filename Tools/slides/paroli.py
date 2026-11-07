"""Python-проєкт «Генератор паролів» (без input)."""
import os
import random
from deck import Deck, c, run, esc, REPO, INK, INK2, ORANGE, BLUE, DARK_BG, PAPER

d = Deck("Генератор паролів", kind="python", topic="Рядки, цикли, random")


def run_seeded(code, seed):
    """Запуск коду з random, але з фіксованим seed — щоб на слайді був справжній вивід."""
    random.seed(seed)
    g = {}
    import contextlib, io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(code.replace("import random\n", ""), {"random": random})
    return buf.getvalue().rstrip("\n")


# 1 — титул
s = d.title("Python", "Генератор паролів", "Рядки, цикли й random",
            notes="Сьогодні проєкт, який реально знадобиться: програма сама придумує надійний пароль і перевіряє, "
                  "чи надійний пароль, який придумали ви. Тут зійдуться цикл, умови, рядки й випадкові числа.")
s.raw(f'<div style="position:absolute;left:1180px;top:200px;width:620px;height:150px;border-radius:28px;'
      f'background:{DARK_BG};box-sizing:border-box;border:2px solid #6A6E75"></div>')
s.text(1180, 200, 620, 150, "Tr7!mq9#Lz", size=72, weight=700, mono=True, color=PAPER, align="center",
       valign="center", extra=";letter-spacing:4px")
for k, col in enumerate(["#D07C36", "#F0A55E", "#A9CBF3", "#2F6FB7"]):
    s.raw(f'<div style="position:absolute;left:{1180 + k * 160}px;top:380px;width:140px;height:20px;border-radius:10px;'
          f'background:{col}"></div>')
s.text(1180, 430, 620, 50, "надійність: висока", size=30, weight=700, color=BLUE)

# 2 — план
d.plan(["Який пароль зламають першим?", "Що робить пароль надійним", "Як працює генератор",
        "Три інструменти", "Крок 1. Набір символів", "Крок 2. Випадковий символ", "Крок 3. Цикл збирає пароль",
        "Скільки варіантів?", "Крок 4. Перевірка надійності", "Повний код і покращення"],
       notes="Спершу розберемося, що таке надійний пароль, потім напишемо генератор крок за кроком, "
             "а наприкінці — перевірку, яка ставить паролю оцінку.")

# 3 — гачок
s = d.slide("Який пароль зламають першим?",
            "Голосування: хто вважає, що 123456 — поганий пароль? А kotyk2012? Пояснюємо: зломщики не вгадують по одному, "
            "програма перебирає мільйони варіантів за секунду, і спершу — найпопулярніші паролі та слова зі словника. "
            "Ім’я кота з роком народження — серед перших. Ніколи не кажемо свої справжні паролі вголос!", dark=True)
s.h2("Який пароль зламають першим?", size=84, top=96, width=1600)
s.sub("Програма-зломщик перебирає мільйони варіантів щосекунди.", size=36)
pw = [("123456", "миттєво — найпопулярніший пароль у світі", "orange"),
      ("qwerty", "миттєво — це просто ряд клавіш", "orange"),
      ("kotyk2012", "швидко — слово зі словника + рік", "orange"),
      ("Tr7!mq9#Lz", "дуже довго — немає слів і закономірностей", "blue")]
for k, (p, why, kind) in enumerate(pw):
    y = 300 + k * 160
    s.box(128, y, 560, 130, "screen")
    s.text(128, y, 560, 130, esc(p), size=48, weight=700, mono=True, color=PAPER, align="center", valign="center")
    with s.frame():
        s.chip(720, y, 1072, 130, why, kind=kind, size=34, mono=False, weight=600)

# 4 — що робить пароль надійним
s = d.slide("Що робить пароль надійним",
            "Чотири ознаки, з яких потім складемо перевірку. Найважливіша — довжина: кожен додатковий символ множить "
            "кількість варіантів. Пароль-фраза з трьох-чотирьох випадкових слів теж буває надійною, бо вона довга.")
s.h2("Що робить пароль надійним")
s.sub("Чотири ознаки — з них потім складемо перевірку.")
crit = [("Довжина", "щонайменше 12 символів", "abcdefghijkl"), ("Великі й малі", "обидва види літер", "aBcD"),
        ("Цифри", "хоча б одна", "0–9"), ("Знаки", "хоча б один", "! @ # $ % & * ?")]
for k, (t, b, ex) in enumerate(crit):
    with s.frame():
        x = 128 + k * 420
        s.card(x, 310, 392, 330, t, [b], kind="blue" if k == 0 else "light", title_size=40, body_size=30,
               valign="flex-start")
        s.text(x + 32, 540, 328, 70, esc(ex), size=30, weight=700, mono=True, color=BLUE)
with s.frame():
    s.card(128, 690, 1664, 170, "І ще одне правило",
           "Ніяких слів, імен, дат народження й «qwerty». Справжній пароль нікому не кажемо — навіть другові.",
           kind="orange", title_size=34, body_size=30)

# 5 — як працює
s = d.slide("Як працює генератор",
            "Пояснюємо на руках: у мішечку всі символи, виймаємо навмання один, записуємо, кладемо назад — і так 12 разів. "
            "Кожен крок цього алгоритму — окремий шматок коду.")
s.h2("Як працює генератор")
flow = [("01", "Набір символів", "усі літери, цифри й знаки в одному рядку"),
        ("02", "Повторити N разів", "цикл " + c("for") + " на потрібну довжину"),
        ("03", "Взяти навмання", c("random.choice") + " — один випадковий символ"),
        ("04", "Дописати", "додаємо символ у кінець пароля")]
for k, (n, t, b) in enumerate(flow):
    with s.frame():
        x = 128 + (k % 2) * 840
        y = 260 + (k // 2) * 300
        s.box(x, y, 800, 260, "blue" if k % 3 == 0 else "light", radius=20)
        s.chip(x + 32, y + 32, 90, 60, n, kind="light", size=30)
        s.text(x + 150, y + 32, 620, 60, f"<b>{t}</b>", size=38, valign="center")
        s.text(x + 32, y + 120, 736, 110, b, size=30, color=INK2)

# 6 — три інструменти
s = d.slide("Три інструменти",
            "Нові для проєкту лише дві речі: модуль random (його детально вивчимо на уроці 22) і оператор in для рядка. "
            "Додавання рядків через += вже знайоме з накопичувача.")
s.h2("Три інструменти")
tools = [("random.choice(рядок)", "бере з рядка один випадковий символ", 'random.choice("abc") → "b"'),
         ("пароль += символ", "дописує символ у кінець рядка", '"ab" + "c" → "abc"'),
         ("символ in рядок", "True, якщо символ є в рядку", '"7" in "0123456789" → True')]
for k, (t, b, ex) in enumerate(tools):
    with s.frame():
        y = 240 + k * 240
        s.box(128, y, 1664, 210, "light", radius=20)
        s.text(168, y, 760, 210, esc(t), size=40, weight=700, mono=True, color=BLUE, valign="center")
        s.text(960, y + 30, 800, 70, b, size=32)
        s.text(960, y + 110, 800, 70, esc(ex), size=28, mono=True, color=INK2)

# 7 — крок 1
code7 = '''літери = "abcdefghijklmnopqrstuvwxyz"
великі = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
цифри = "0123456789"
знаки = "!@#$%&*?"

всі = літери + великі + цифри + знаки
print(len(всі))'''
s = d.slide("Крок 1. Набір символів",
            "Записуємо всі символи, з яких можна складати пароль, у чотири рядки, а потім склеюємо в один. "
            "len показує, скільки всього символів у «мішечку»: 26 + 26 + 10 + 8 = 70.")
s.h2("Крок 1. Набір символів")
s.sub("Усе, з чого складатиметься пароль, — в одному рядку.")
s.code(128, 300, 1100, 480, code7, size=28)
with s.frame():
    s.screen(1260, 300, 532, 130, run(code7))
with s.frame():
    s.card(1260, 460, 532, 320, "26 + 26 + 10 + 8",
           ["малі + великі + цифри + знаки = <b>70 символів</b> у «мішечку»"], kind="blue",
           title_size=36, body_size=30)

# 8 — крок 2
code8 = '''import random

цифри = "0123456789"
print(random.choice(цифри))
print(random.choice(цифри))
print(random.choice(цифри))'''
s = d.slide("Крок 2. Випадковий символ",
            "random.choice бере один випадковий символ із рядка. Запускаємо кілька разів — щоразу інший результат. "
            "import random пишемо один раз, на самому початку програми.")
s.h2("Крок 2. Випадковий символ")
s.sub(c("random.choice") + " виймає з «мішечка» один символ навмання.")
s.code(128, 300, 1000, 400, code8, size=30)
with s.frame():
    s.screen(1160, 300, 300, 260, run_seeded(code8, 3), label="ЗАПУСК 1")
    s.screen(1492, 300, 300, 260, run_seeded(code8, 11), label="ЗАПУСК 2")
with s.frame():
    s.card(1160, 590, 632, 200, "Щоразу інакше",
           "Той самий код — різний результат. Саме це й потрібно для пароля.", kind="blue", title_size=34,
           body_size=28)
with s.frame():
    s.card(128, 730, 1000, 150, None, c("import random") + " — один раз, на самому початку програми.",
           kind="orange", body_size=30)

# 9 — крок 3
code9 = '''import random

всі = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%&*?"
довжина = 12

пароль = ""
for i in range(довжина):
    пароль += random.choice(всі)

print(пароль)'''
s = d.slide("Крок 3. Цикл збирає пароль",
            "Це той самий накопичувач, тільки накопичуємо не суму, а рядок. Пароль спершу порожній, а на кожному кроці "
            "в кінець дописується один випадковий символ. Хочете довший пароль — міняємо одне число.")
s.h2("Крок 3. Цикл збирає пароль")
s.sub("Накопичувач, тільки замість суми — рядок.")
s.code(128, 290, 1220, 470, code9.replace(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%&*?", "…усі 70 символів…"), size=26, lh=1.45)
with s.frame():
    trace = ["", "k", "k7", "k7#", "k7#R", "…"]
    s.screen(1380, 290, 412, 470, "\n".join(f"крок {i}: {t!r}" if i < 5 else "…" for i, t in enumerate(trace)),
             label="ЯК РОСТЕ ПАРОЛЬ", size=26, valign="flex-start")
with s.frame():
    s.screen(128, 790, 800, 120, run_seeded(code9, 7), label="ЕКРАН")
with s.frame():
    s.card(960, 790, 832, 120, None, "Довший пароль? Міняємо " + c("довжина = 16") + ".", kind="blue", body_size=30)

# 10 — скільки варіантів
s = d.slide("Скільки варіантів?",
            "Чому довжина така важлива. 4 цифри — лише 10 тисяч варіантів, комп’ютер перебере їх миттєво. "
            "8 символів із 70 — це 70 у восьмому степені, близько 576 трильйонів. Кожен новий символ множить варіанти ще в 70 разів.",
            dark=True)
s.h2("Скільки варіантів?", size=72, top=190, width=700)
s.text(128, 420, 620, 300, ["PIN-код із 4 цифр:", "<b>10 000</b> варіантів — перебір за мить.", "",
                            "Кожен новий символ множить кількість варіантів у <b>70 разів</b>."],
       size=30, color="#BFC6D0", lh=1.45)
s.raw('<div style="position:absolute;left:900px;top:100px;width:840px;height:840px;border-radius:50%;'
      'background:radial-gradient(circle at 40% 35%, rgba(213,219,227,0.55) 0%, rgba(156,192,239,0.38) 60%, '
      'rgba(156,192,239,0.18) 100%);border:2px solid rgba(238,241,245,0.35)"></div>')
assert 70 ** 8 == 576480100000000
s.raw(f'<h1 style="position:absolute;left:900px;top:330px;width:840px;font-size:200px;font-weight:800;line-height:1;'
      f'color:{PAPER};text-align:center;letter-spacing:-6px;">70<sup style="font-size:110px">8</sup></h1>')
s.text(1040, 580, 560, 120, "≈ 576 трильйонів паролів із 8 символів", size=32, weight=600, color=PAPER,
       align="center")
with s.frame("pop"):
    s.raw('<div style="position:absolute;left:700px;top:640px;width:340px;height:340px;border-radius:50%;'
          'background:#E6EAF0;box-shadow:0 12px 48px rgba(20,24,30,0.3);display:flex;flex-direction:column;'
          'align-items:center;justify-content:center;gap:8px;padding:0px 36px">'
          f'<p style="font-size:110px;font-weight:800;line-height:1;color:{INK};text-align:center;">10<sup style="font-size:56px">4</sup></p>'
          f'<p style="font-size:24px;font-weight:400;line-height:1.3;color:{INK2};text-align:center;">варіантів у PIN-коду</p></div>')

# 11 — крок 4
check = '''пароль = "Kotyk2012"

великі = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
цифри = "0123456789"
знаки = "!@#$%&*?"

є_велика = False
є_цифра = False
є_знак = False
for символ in пароль:
    if символ in великі:
        є_велика = True
    elif символ in цифри:
        є_цифра = True
    elif символ in знаки:
        є_знак = True

бали = 0
if len(пароль) >= 12:
    бали += 1
if є_велика:
    бали += 1
if є_цифра:
    бали += 1
if є_знак:
    бали += 1

if бали == 4:
    print("Надійний")
elif бали >= 2:
    print("Середній")
else:
    print("Слабкий")'''
s = d.slide("Крок 4. Перевірка надійності",
            "Друга частина проєкту — оцінити пароль. Прапорці (урок 5) запам’ятовують, чи траплялася велика літера, "
            "цифра, знак. Цикл for іде по кожному символу пароля. Потім рахуємо бали й ставимо оцінку ланцюжком elif. "
            "Для Kotyk2012: є велика, є цифра, знаку немає, довжина 9 — 2 бали, «Середній».")
s.h2("Крок 4. Перевірка надійності", size=64)
left, right = check.split("\nбали = 0\n")
s.code(128, 200, 840, 860, left, size=23, lh=1.42)
s.code(992, 200, 520, 860, "бали = 0\n" + right, size=23, lh=1.42)
with s.frame():
    s.card(1540, 200, 252, 250, "Прапорці", "запам’ятовують, що знайшли", kind="blue", title_size=28, body_size=24,
           pad=20)
with s.frame():
    s.card(1540, 470, 252, 250, "Бали", "+1 за кожну ознаку", kind="orange", title_size=28, body_size=24, pad=20)
with s.frame():
    s.screen(1540, 740, 252, 150, run(check), size=26)

# 12 — повний код
full_gen = '''import random

літери = "abcdefghijklmnopqrstuvwxyz"
великі = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
цифри = "0123456789"
знаки = "!@#$%&*?"
всі = літери + великі + цифри + знаки

довжина = 12
пароль = ""
for i in range(довжина):
    пароль += random.choice(всі)

print("Ваш пароль:", пароль)'''
s = d.slide("Повний код генератора",
            "Генератор цілком — 13 рядків. Перевірку з кроку 4 можна поставити одразу після нього й перевіряти "
            "щойно згенерований пароль. Питаємо: чи завжди генератор дає надійний пароль? Ні! Може випадково не трапитися "
            "жодної цифри — це перше покращення.")
s.h2("Повний код генератора")
s.code(128, 214, 1100, 760, full_gen, size=27)
with s.frame():
    s.text(1270, 230, 522, 300, ["<b>13 рядків</b> — і генератор готовий.",
                                 "Перевірку з кроку 4 ставимо одразу після нього."], size=32, lh=1.35)
with s.frame():
    s.screen(1270, 500, 522, 130, run_seeded(full_gen, 21), size=26)
with s.frame():
    s.card(1270, 660, 522, 260, "Чи завжди надійний?",
           "Ні! Цифри може випадково не трапитися жодної. Як це виправити — на наступному слайді.",
           kind="orange", title_size=30, body_size=27)

# 13 — що скаже перевірка
s = d.slide("Що скаже перевірка?",
            "Клас голосує за кожен пароль: слабкий, середній чи надійний. Потім відкриваємо. "
            "Цікавий випадок — довгий пароль із самих малих літер: довжина є, а інших ознак немає.")
s.h2("Що скаже перевірка?")
s.sub("Програма з кроку 4. Голосуємо: слабкий, середній чи надійний?")
tests = ["qwerty", "Kotyk2012", "dovgyiparolbezcyfr", "Tr7!mq9#Lz-Sun"]
for k, p in enumerate(tests):
    y = 300 + k * 160
    s.box(128, y, 900, 130, "screen")
    s.text(128, y, 900, 130, esc(p), size=40, weight=700, mono=True, color=PAPER, align="center", valign="center")
for k, p in enumerate(tests):
    y = 300 + k * 160
    verdict = run(check.replace('"Kotyk2012"', repr(p).replace("'", '"'), 1))
    kind = {"Слабкий": "orange", "Середній": "light", "Надійний": "blue"}[verdict]
    with s.frame("pop"):
        s.chip(1060, y, 732, 130, verdict, kind=kind, size=40, mono=False, weight=700)

# 14 — покращуємо
s = d.slide("Покращуємо генератор",
            "Рівні для тих, хто впорався швидко. Рівень 1 — найважливіший: генеруємо, доки перевірка не скаже «Надійний» "
            "(знадобиться while з уроку 14) або просто дописуємо по одному символу кожного виду. Рівень 4 — пароль-фраза, "
            "що легко запам’ятати.")
s.h2("Покращуємо генератор")
lv = [("Рівень 1", "Гарантія", "у паролі завжди є хоча б одна цифра і один знак"),
      ("Рівень 2", "П’ять варіантів", "цикл генерує 5 паролів — обирай, який подобається"),
      ("Рівень 3", "Без плутанини", "прибрати схожі символи: 0 і O, 1, l та I"),
      ("Рівень 4", "Пароль-фраза", "4 випадкові слова зі списку: " + c("кіт-ракета-сир-хмара"))]
for k, (lvl, t, b) in enumerate(lv):
    with s.frame():
        x = 128 + k * 420
        s.chip(x, 240, 392, 70, lvl, kind="blue", size=30, mono=False, weight=700)
        s.card(x, 340, 392, 420, t, b, kind="light", title_size=34, body_size=28, valign="flex-start")
with s.frame():
    s.note(820, "Підказка до рівня 1: допишіть у кінець " + c("random.choice(цифри)") + " і " +
           c("random.choice(знаки)") + ".")

# 15 — типові помилки
s = d.slide("Типові помилки",
            "Перша — Python скаже NameError: name 'random' is not defined. Друга — random.choice викликали один раз до циклу, "
            "тож увесь пароль складається з одного символу. Третя — пароль = \"\" усередині циклу: щоразу стирається, "
            "і в кінці лишається один символ.")
s.text(128, 420, 560, 240, "Типові<br/>помилки", size=96, weight=700, lh=1.02, extra=";letter-spacing:-3px")
s.text(128, 860, 540, 120, "Друга й третя підступні: Python не сварить, а пароль виходить поганий.", size=26,
       color=INK2, lh=1.35)
with s.frame():
    s.mistake(720, 130, 1072, '''пароль += random.choice(всі)
# NameError: name 'random' ...''', "Забули " + c("import random") + " на початку програми", code_h=110, size=26)
with s.frame():
    s.mistake(720, 380, 1072, '''символ = random.choice(всі)
for i in range(12):
    пароль += символ''', "Вибір поза циклом: вийде " + c("kkkkkkkkkkkk"), code_h=150, size=26)
with s.frame():
    s.mistake(720, 670, 1072, '''for i in range(12):
    пароль = ""
    пароль += random.choice(всі)''', c('пароль = ""') + " у циклі — пароль щоразу стирається", code_h=150, size=26)

# 16 — ваш хід
d.your_turn([("key", "Генератор: пароль на 12 символів"), ("lock", "Перевірка: оцініть 5 різних паролів"),
             ("check", "Гарантія: завжди є цифра і знак"), ("list", "Пароль-фраза з чотирьох слів"),
             ("star", "⭐ Дайте сусідові перевірити ваш генератор")],
           notes="Обов’язкові — перші два пункти: генератор і перевірка. Решта — рівні покращення. "
                 "Справжні паролі в класі не використовуємо й нікому не показуємо.")

out = os.path.join(REPO, "Презентації уроків", "Python", "Проєкти", "Генератор паролів.html")
print(d.save(out), len(d.slides))
