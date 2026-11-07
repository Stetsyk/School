"""Спільне для графічних колод (уроки 24–29): заготовка програми на полотні."""


def prog(body, w=600, h=400, title="Малюнок", bg="white", extra_import=""):
    """Повна програма для запуску; на слайді зазвичай показуємо лише body."""
    imp = "import tkinter\n" + extra_import
    return (f'{imp}\nвікно = tkinter.Tk()\nвікно.title("{title}")\n'
            f'полотно = tkinter.Canvas(вікно, width={w}, height={h}, bg="{bg}")\nполотно.pack()\n\n'
            f'{body.strip()}\n\nвікно.mainloop()\n')
