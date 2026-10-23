# Гра Bounce. Урок 3: життя, рівні й швидкість

import tkinter
import time
import random

вікно = tkinter.Tk()
вікно.title("Bounce")
полотно = tkinter.Canvas(вікно, width=600, height=400, bg="midnightblue")
полотно.pack()

табло = полотно.create_text(120, 20, text="Рахунок: 0   Рівень: 1",
                            fill="white", font=("Arial", 14))
серця = полотно.create_text(540, 20, text="♥♥♥",
                            fill="red", font=("Arial", 18))
мяч = полотно.create_oval(100, 50, 130, 80, fill="orange")
ракетка = полотно.create_rectangle(250, 370, 350, 385, fill="white")


def ліворуч(подія):
    x1, y1, x2, y2 = полотно.coords(ракетка)
    if x1 > 0:
        полотно.move(ракетка, -25, 0)


def праворуч(подія):
    x1, y1, x2, y2 = полотно.coords(ракетка)
    if x2 < 600:
        полотно.move(ракетка, 25, 0)


полотно.bind("<Left>", ліворуч)
полотно.bind("<Right>", праворуч)
полотно.focus_set()

кольори = ["orange", "yellow", "lime", "cyan", "violet", "red"]
dx = 5
dy = 4
рахунок = 0
рівень = 1
життя = 3

while життя > 0:
    полотно.move(мяч, dx, dy)
    x1, y1, x2, y2 = полотно.coords(мяч)

    if x1 <= 0 or x2 >= 600:
        dx = -dx
    if y1 <= 0:
        dy = -dy

    if ракетка in полотно.find_overlapping(x1, y1, x2, y2) and dy > 0:
        dy = -dy
        рахунок = рахунок + 1
        полотно.itemconfig(мяч, fill=random.choice(кольори))
        # кожні 5 очок — новий рівень, м'яч швидшає
        if рахунок % 5 == 0:
            рівень = рівень + 1
            dx = dx * 1.2
            dy = dy * 1.2
        полотно.itemconfig(табло, text=f"Рахунок: {рахунок}   Рівень: {рівень}")

    # м'яч упав — мінус одне життя, м'яч повертається нагору
    if y2 >= 400:
        життя = життя - 1
        полотно.itemconfig(серця, text="♥" * життя)
        полотно.coords(мяч, 285, 50, 315, 80)
        полотно.update()
        time.sleep(1)

    полотно.update()
    time.sleep(0.02)

полотно.create_text(300, 200, text=f"Гру завершено!\nРахунок: {рахунок}",
                    fill="white", font=("Arial", 30), justify="center")
вікно.mainloop()
