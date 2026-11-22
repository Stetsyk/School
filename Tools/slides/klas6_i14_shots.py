"""Справжні скріни Krita для колоди 6 клас, урок І-14 «Шари» (імпортується з klas6_i14.py).
Краєвид із семи шарів (shary6.py) кладемо в Krita справжніми шарами, далі — клацання й набір назв xdotool."""
import shary6 as h
from kritakroky import kk, box, row_box, LAYERS, LAYER_PANEL, DOC_1200, FILE_MENU, AWAY

PANEL = LAYER_PANEL
Z = 0.7                                 # у кадрах «полотно + шари» полотно менше, щоб панель вийшла більшою
ROW = [h.doc_rect(Z), (1100, 336, 1366, 622)]


def land(**kw):
    kw.setdefault("zoom", Z)
    st = h.land_steps(**kw)
    st.insert(1, {"hide_docker": "PresetDocker"})
    return st


# рядки панелі зверху вниз: 0 підпис · 1 дерево · 2 будинок · 3 хмара · 4 сонце · 5 трава · 6 небо
TITLE = kk(land(active="хмара", zoom=1.3), [AWAY], parts=[DOC_1200])
STACK = kk(land(active="підпис"), [AWAY], parts=ROW, layout="row",
           marks=[row_box(0, "row", "right"), row_box(6, "row", "right")])
PANEL5 = kk(land(active="хмара"), [AWAY], parts=[PANEL],
            marks=[box(LAYERS["+"], "top"), row_box(3, "name", "right"), row_box(3, "eye", "left"),
                   box((1184, 708, 1241, 732), "top"), box(LAYERS["Непрозорість"], "left")])

# новий шар і перейменування: + → «Шар 2» → подвійний клік → набираємо «небо»
NEW = [{"new": [1200, 900, "Краєвид — Прізвище"]}, {"hide_docker": "PresetDocker"}, {"zoom": 1.3}, {"layer": "Шар 2"}]
RENAME = kk(NEW, ["mousemove 1230 439", "click --repeat 2 1", "sleep 0.8", "key ctrl+a", "type --delay 300 небо",
                  "sleep 0.8", AWAY],
            parts=[(1100, 336, 1366, 500), (1100, 690, 1366, 742)],
            marks=[box(LAYERS["+"], "top"), box((1130, 427, 1362, 451), "right")])

ACTIVE = kk(land(active="дерево"), [AWAY], parts=ROW, layout="row", marks=[row_box(1, "row", "right")])
EYE_ON = kk(land(active="хмара"), [AWAY], parts=ROW, layout="row", marks=[row_box(3, "eye", "left")])
EYE_OFF = kk(land(active="хмара", hidden=["хмара"]), [AWAY], parts=ROW, layout="row", marks=[row_box(3, "eye", "left")])

BAD = h.LAND[:]
BAD.remove("трава")
BAD.append("трава")                     # траву перетягнули на самий верх
ORDER_BAD = kk(land(order=BAD, active="трава"), [AWAY], parts=ROW, layout="row", marks=[row_box(0, "row", "right")])
MOVE = kk(land(order=BAD, active="трава"), [AWAY], parts=[PANEL],
          marks=[row_box(0, "row", "right"), box(LAYERS["Нижче"], "top")])

OPACITY = kk(land(active="хмара", opacity={"хмара": 50}), [AWAY], parts=ROW, layout="row",
             marks=[row_box(3, "row", "right"), box(LAYERS["Непрозорість"], "right")])
FILE = kk(land(active="хмара", zoom=1.3), ["mousemove 25 10", "click 1", "sleep 1"], parts=[(0, 0, 412, 232)],
          marks=[box(FILE_MENU["Зберегти як"], "right"), box(FILE_MENU["Експортувати"], "right")])

if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.isupper() and isinstance(v, str) and v.endswith(".png"):
            print(k, v)
