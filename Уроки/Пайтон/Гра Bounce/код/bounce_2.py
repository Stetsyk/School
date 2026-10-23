# Гра Bounce. Урок 2: ракетка, рахунок і кінець гри

import tkinter
import time

вікно = tkinter.Tk()
вікно.title("Bounce")
полотно = tkinter.Canvas(вікно, width=600, height=400, bg="midnightblue")
полотно.pack()

табло = полотно.create_text(300, 20, text="Рахунок: 0",
                            fill="white", font=("Arial", 14))
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

dx = 5
dy = 4
рахунок = 0

while True:
    полотно.move(мяч, dx, dy)
    x1, y1, x2, y2 = полотно.coords(мяч)

    # стіни: ліва, права і верхня
    if x1 <= 0 or x2 >= 600:
        dx = -dx
    if y1 <= 0:
        dy = -dy

    # ракетка: чи торкається вона м'яча?
    if ракетка in полотно.find_overlapping(x1, y1, x2, y2) and dy > 0:
        dy = -dy
        рахунок = рахунок + 1
        полотно.itemconfig(табло, text=f"Рахунок: {рахунок}")

    # м'яч упав на дно — кінець гри
    if y2 >= 400:
        break

    полотно.update()
    time.sleep(0.02)

полотно.create_text(300, 200, text=f"Гру завершено!\nРахунок: {рахунок}",
                    fill="white", font=("Arial", 30), justify="center")
вікно.mainloop()
