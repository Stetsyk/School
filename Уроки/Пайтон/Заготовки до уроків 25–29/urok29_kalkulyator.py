# Урок 29, рівень 2. Калькулятор на повзунках.
# Вікно й функція плюс() уже готові. Допишіть мінус(), помножити() і поділити() за зразком плюса:
# взяти два числа — порахувати — показати в написі. Поки функцію не дописано, кнопка нічого не робить.
import tkinter

вікно = tkinter.Tk()
вікно.title("Калькулятор")
вікно.geometry("440x330")
вікно.option_add("*Font", ("Arial", 20))


def плюс():
    a = повзунок1.get()
    b = повзунок2.get()
    напис.config(text=f"{a} + {b} = {a + b}")


def мінус():
    pass    # допишіть за зразком плюс()


def помножити():
    pass    # допишіть


def поділити():
    pass    # допишіть; ⭐ ділення на нуль — рівень 3


повзунок1 = tkinter.Scale(вікно, from_=0, to=20, orient="horizontal", length=360)
повзунок1.pack()
повзунок2 = tkinter.Scale(вікно, from_=0, to=20, orient="horizontal", length=360)
повзунок2.pack()

рядок = tkinter.Frame(вікно)
рядок.pack(pady=10)
tkinter.Button(рядок, text="+", command=плюс).pack(side="left")
tkinter.Button(рядок, text="−", command=мінус).pack(side="left")
tkinter.Button(рядок, text="×", command=помножити).pack(side="left")
tkinter.Button(рядок, text="÷", command=поділити).pack(side="left")

напис = tkinter.Label(вікно, text="Оберіть числа")
напис.pack(pady=10)

вікно.mainloop()
