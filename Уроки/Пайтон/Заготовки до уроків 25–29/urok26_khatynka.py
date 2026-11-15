# Урок 26. Готова функція-штамп «хатинка».
# Функцію не змінюйте — просто викликайте її внизу з різними x, y і кольором.
# Полотно 600 × 400: якщо хатинка вилізла за край — зменште x або y.
import tkinter
import random

вікно = tkinter.Tk()
вікно.title("Вулиця")

полотно = tkinter.Canvas(вікно, width=600, height=400, bg="white")
полотно.pack()


def хатинка(x, y, колір):
    полотно.create_rectangle(x, y, x + 100, y + 80, fill=колір)
    полотно.create_polygon(x - 10, y, x + 50, y - 50, x + 110, y,
                           fill="brown")
    полотно.create_rectangle(x + 40, y + 40, x + 60, y + 80,
                             fill="saddlebrown")
    полотно.create_rectangle(x + 10, y + 15, x + 30, y + 35,
                             fill="lightblue")


def дерево(x, y):
    полотно.create_rectangle(x - 6, y - 40, x + 6, y,
                             fill="sienna")
    полотно.create_oval(x - 30, y - 100, x + 30, y - 30,
                        fill="forestgreen")


# ---------- ВАШ КОД ----------
# Рівень 1: поставте 3–4 хатинки, наприклад:
хатинка(40, 220, "pink")
хатинка(240, 120, "lightblue")
хатинка(440, 260, "wheat")

# Рівень 2: цикл, що ставить 5 хатинок у ряд, і дерева — див. презентацію.

# ---------- ВАШ КОД ----------

вікно.mainloop()
