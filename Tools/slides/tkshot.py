"""Запускає приклад на tkinter/turtle під віртуальним дисплеєм і знімає справжній скриншот вікна.

Запуск (робить grafika.py): xvfb-run python3.12 tkshot.py приклад.py вихід.png [сценарій.json]
Сценарій — список дій після старту: {"click": [x, y]}, {"key": "Left"}, {"drag": [[x,y],...]},
{"type": [номер_поля, "текст"]}, {"button": номер}, {"steps": N} — скільки кадрів анімації прокрутити.
"""
import json
import subprocess
import sys
import time
import tkinter

REAL_SLEEP = time.sleep
src, out = sys.argv[1], sys.argv[2]
scenario = json.loads(open(sys.argv[3]).read()) if len(sys.argv) > 3 else []
steps_limit = next((a["steps"] for a in scenario if "steps" in a), None)


class Done(Exception):
    pass


def find_root():
    return tkinter._default_root


def snap():
    root = find_root()
    for _ in range(5):
        root.update()
        REAL_SLEEP(0.05)
    # верхнє вікно (без менеджера вікон рамки немає)
    top = root.wm_frame()
    subprocess.run(["import", "-window", top, out], check=True)
    with open(out + ".title", "w") as f:
        f.write(root.title())
    raise Done


def widgets(root, cls):
    res = []
    stack = [root]
    while stack:
        w = stack.pop(0)
        if isinstance(w, cls):
            res.append(w)
        stack.extend(w.winfo_children())
    return res


_played = [False]


def play():
    if _played[0]:
        raise Done
    _played[0] = True
    root = find_root()
    root.update()
    for a in scenario:
        canvases = widgets(root, tkinter.Canvas)
        tgt = canvases[0] if canvases else root
        if "click" in a:
            x, y = a["click"]
            tgt.event_generate("<Button-1>", x=x, y=y)
            tgt.event_generate("<ButtonRelease-1>", x=x, y=y)
        elif "drag" in a:
            pts = a["drag"]
            tgt.event_generate("<Button-1>", x=pts[0][0], y=pts[0][1])
            for x, y in pts[1:]:
                tgt.event_generate("<B1-Motion>", x=x, y=y)
            tgt.event_generate("<ButtonRelease-1>", x=pts[-1][0], y=pts[-1][1])
        elif "motion" in a:
            x, y = a["motion"]
            tgt.event_generate("<Motion>", x=x, y=y)
        elif "key" in a:
            tgt.focus_force()
            root.update()
            tgt.event_generate(f"<{a['key']}>" if len(a["key"]) > 1 else a["key"])
        elif "type" in a:
            i, txt = a["type"]
            e = widgets(root, tkinter.Entry)[i]
            e.delete(0, "end")
            e.insert(0, txt)
        elif "scale" in a:
            i, v = a["scale"]
            widgets(root, tkinter.Scale)[i].set(v)
        elif "button" in a:
            widgets(root, tkinter.Button)[a["button"]].invoke()
        root.update()
    snap()


_orig_mainloop = tkinter.Misc.mainloop


def fake_mainloop(self, n=0):
    play()


tkinter.Misc.mainloop = fake_mainloop
tkinter.mainloop = lambda n=0: play()

# messagebox не блокує, а показує текст у заголовку скриншота
from tkinter import messagebox  # noqa: E402
for name in ("showinfo", "showwarning", "showerror"):
    setattr(messagebox, name, lambda t, m, _n=name: open(out + ".msg", "w").write(f"{_n}|{t}|{m}"))

# анімації: рахуємо кадри через time.sleep
_count = [0]
_real_sleep = time.sleep


def fake_sleep(s):
    _count[0] += 1
    if steps_limit is not None and _count[0] >= steps_limit:
        play()


time.sleep = fake_sleep

code = open(src, encoding="utf-8").read()

# turtle: малюємо миттєво й знімаємо в done()
if "turtle" in code:
    import turtle
    _setup = turtle.setup
    turtle.setup(640, 480)
    turtle.tracer(0, 0)
    turtle.done = turtle.mainloop = lambda: (turtle.update(), play())
    turtle.speed = lambda *a, **k: None
try:
    exec(compile(code, src, "exec"), {"__name__": "__main__"})
    play()
except Done:
    pass
