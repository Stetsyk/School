# Гра Bounce. Урок 1: м'яч, що б'ється об стіни й полює на кути

import tkinter
import time
import random

вікно = tkinter.Tk()
вікно.title("Bounce")
полотно = tkinter.Canvas(вікно, width=600, height=400, bg="midnightblue")
полотно.pack()

напис = полотно.create_text(300, 200, text="", fill="yellow", font=("Arial", 60))
табло = полотно.create_text(300, 20, text="Удари: 0   Кути: 0",
                            fill="white", font=("Arial", 14))
мяч = полотно.create_oval(100, 50, 130, 80, fill="orange")

кольори = ["orange", "yellow", "lime", "cyan", "violet", "red"]
dx = 5
dy = 4
удари = 0
кути = 0

while True:
    полотно.move(мяч, dx, dy)
    x1, y1, x2, y2 = полотно.coords(мяч)

    # ліва або права стіна
    if x1 <= 0 or x2 >= 600:
        dx = -dx
        удари = удари + 1
        полотно.itemconfig(мяч, fill=random.choice(кольори))
        полотно.itemconfig(напис, text="")
        # м'яч біля верху або низу — значить, це кут
        if y1 <= 20 or y2 >= 380:
            кути = кути + 1
            полотно.itemconfig(напис, text="КУТ!")

    # верхня або нижня стіна
    if y1 <= 0 or y2 >= 400:
        dy = -dy
        удари = удари + 1
        полотно.itemconfig(мяч, fill=random.choice(кольори))

    полотно.itemconfig(табло, text=f"Удари: {удари}   Кути: {кути}")
    полотно.update()
    time.sleep(0.02)
