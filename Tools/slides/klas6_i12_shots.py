"""Скриншоти Krita для колоди 6 клас, урок І-12 (растрові зображення). Імпортується з klas6_i12.py."""
import grafika6 as g
from grafika6 import scr, stroke, smile_points
from kritashot import kshot

E0 = g.save_emoji(0, 500, "porozhnie_500.png")
E1 = g.save_emoji(1, 500)
E3 = g.save_emoji(3, 500)
E4 = g.save_emoji(4, 500)
GAP = g.ring_with_gap(True)
NOGAP = g.ring_with_gap(False)
AWAY = "mousemove 1300 740"
FILL = "KritaFill/KisToolFill"

# інтерфейс з готовим емодзі
K_UI = kshot([{"open": E4}, {"zoom": 1.0}, {"tool": "KisToolBrush"}], xdo=[AWAY])

# Файл → Створити 500 × 500, вкладки «Розміри» і «Вміст»
NEW = [{"open": E4}, {"action": "file_new", "async": True, "delay": 3000}]
TYPE500 = ["mousemove 757 185", "click 1", "key ctrl+a", "type 500", "key Tab", "mousemove 757 217", "click 1",
           "key ctrl+a", "type 500", "key Tab", "sleep 0.6"]
K_NEW = kshot(NEW, xdo=TYPE500)
K_NEW_CONTENT = kshot(NEW, xdo=TYPE500 + ["mousemove 647 85", "click 1", "sleep 1"])

# овальне виділення: тягнемо мишкою справжнім інструментом
x0, y0 = scr(40, 40)
x1, y1 = scr(460, 460)
SEL = [f"mousemove {x0} {y0}", "mousedown 1", f"mousemove {(x0 + x1) // 2} {(y0 + y1) // 2}", f"mousemove {x1} {y1}",
       "mouseup 1", "sleep 0.6"]
K_SEL = kshot([{"open": E0}, {"zoom": 1.0}, {"tool": "KisToolSelectElliptical"}], xdo=SEL + [AWAY])
cx, cy = scr(250, 250)
K_SEL_FILL = kshot([{"open": E0}, {"zoom": 1.0}, {"fg": "#F7CE46"}, {"tool": "KisToolSelectElliptical"}],
                   xdo=SEL + ["key f", "sleep 0.5", f"mousemove {cx} {cy}", "click 1", "sleep 1.5", AWAY])

# заливка: з щілиною й без
K_GAP = kshot([{"open": GAP}, {"zoom": 1.0}, {"fg": "#F7CE46"}, {"tool": FILL}], xdo=[AWAY])
K_LEAK = kshot([{"open": GAP}, {"zoom": 1.0}, {"fg": "#F7CE46"}, {"tool": FILL}],
               xdo=[f"mousemove {cx} {cy}", "click 1", "sleep 1.5", AWAY])
K_NOLEAK = kshot([{"open": NOGAP}, {"zoom": 1.0}, {"fg": "#F7CE46"}, {"tool": FILL}],
                 xdo=[f"mousemove {cx} {cy}", "click 1", "sleep 1.5", AWAY])

# пензель: очі й усмішка справжніми мазками
BRUSH = (stroke([(180, 168), (180, 222)]) + stroke([(320, 168), (320, 222)]) + stroke(smile_points()))
K_BRUSH = kshot([{"open": E1}, {"zoom": 1.0}, {"tool": "KisToolBrush"}, {"fg": "#2F3033"}, {"size": 16}],
                xdo=BRUSH + [AWAY])

# виділення ока для копіювання
K_EYE = kshot([{"open": E4}, {"zoom": 1.0}, {"select_rect": [150, 150, 62, 90]}, {"tool": "KisToolSelectRectangular"}],
              xdo=[AWAY])

# меню «Файл»
K_FILE = kshot([{"open": E4}, {"zoom": 1.0}], xdo=["mousemove 27 10", "click 1", "sleep 1"])

# ---- покрокові скріни з номерами (kritakroky, чіткі scale=2) ----
from kritakroky import kk, box, TOOL, COLOR

DLG = (360, 66, 1005, 632)
KR_NEW = kk(NEW, TYPE500, parts=[DLG],
            marks=[(700, 172, 820, 193, "right"), (700, 204, 820, 225, "right"), (618, 78, 676, 98, "right"),
                   (805, 592, 893, 617, "left")], nums=(3, 3, 4, 5))
KR_CIRCLE = kk([{"open": E0}, {"zoom": 2.0}, {"fg": "#F7CE46"}, {"tool": "KisToolSelectElliptical"}],
               SEL + ["key f", "sleep 0.5", f"mousemove {cx} {cy}", "click 1", "sleep 1.5", AWAY], layout="row",
               parts=[(0, 75, 62, 470), (330, 150, 830, 650), (1104, 90, 1366, 215)],
               marks=[box(TOOL["Еліптичне виділення"], "right"), (x0 + 30, y0 + 30, x1 - 30, y1 - 30, "top"), box(COLOR, "left"),
                      box(TOOL["Заливка"], "right"), (cx - 14, cy - 14, cx + 14, cy + 14, "bottom")])
KR_BRUSH = kk([{"open": E1}, {"zoom": 2.0}, {"tool": "KisToolBrush"}, {"fg": "#2F3033"}, {"size": 16}],
              BRUSH + [AWAY], layout="row",
              parts=[(0, 75, 62, 340), (940, 24, 1180, 56), (330, 150, 830, 650)],
              marks=[box(TOOL["Пензель"], "right"), (960, 28, 1170, 52, "bottom"), box(TOOL["Піпетка"], "right")],
              nums=(1, 2, 3))
