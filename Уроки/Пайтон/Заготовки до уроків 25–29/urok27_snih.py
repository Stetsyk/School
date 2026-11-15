# Урок 27, рівень 3. Сніг падає безкінечно.
# Спробуйте змінити: кількість сніжинок (40), швидкість (3), розмір (8), колір і фон.
import tkinter
import random
import time

вікно = tkinter.Tk()
вікно.title("Сніг")

полотно = tkinter.Canvas(вікно, width=600, height=400, bg="midnightblue")
полотно.pack()

сніжинки = []
for i in range(40):
    x = random.randint(0, 600)
    y = random.randint(-400, 0)
    s = полотно.create_oval(x, y, x + 8, y + 8, fill="white")
    сніжинки.append(s)

while True:
    for s in сніжинки:
        полотно.move(s, 0, 3)
        if полотно.coords(s)[1] > 400:      # упала за низ —
            полотно.move(s, 0, -410)        # повертаємо нагору
    полотно.update()
    time.sleep(0.03)
