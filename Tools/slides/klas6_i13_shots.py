"""Скриншоти Krita для колоди 6 клас, урок І-13 (векторні зображення). Імпортується з klas6_i13.py."""
import grafika6 as g
from kritashot import kshot

AWAY = "mousemove 1300 740"
SEL = "InteractionTool"


def vec(svg, name, sel=None, xdo=None):
    st = [{"new": [500, 500, name]}, {"svg": svg}, {"zoom": 1.0}, {"tool": SEL}]
    if sel:
        st.append({"select_shapes": sel})
    return kshot(st, xdo=xdo or [AWAY])


V_HOUSE_SEL = vec(g.HOUSE_SVG, "Будинок", ["dakh"])
V_HOUSE_BLUE = vec(g.HOUSE_SVG.replace('id="dakh" points="90,235 410,235 250,100" fill="#D9342B"',
                                       'id="dakh" points="90,235 410,235 250,100" fill="#2F6FB7"'), "Будинок", ["dakh"])
V_DROP = vec(g.HOUSE_SVG, "Будинок", None, ["mousemove 1141 445", "click 1", "sleep 1.2"])
V_ROCKET = vec(g.ROCKET_SVG, "Ракета")
V_ROCKET_ONE = vec(g.ROCKET_SVG, "Ракета", ["korpus"])
V_ROCKET_ALL = vec(g.ROCKET_SVG, "Ракета", True)
V_STROKE = vec(g.ROCKET_SVG, "Ракета", ["korpus"], ["mousemove 1305 71", "click 1", "sleep 0.8", "mousemove 1172 117",
                                                   "click 1", "sleep 1"])
V_FILL = vec(g.ROCKET_SVG, "Ракета", ["korpus"], ["mousemove 1305 71", "click 1", "sleep 0.8", "mousemove 1216 117",
                                                 "click 1", "sleep 1"])
V_CTX = vec(g.ROCKET_SVG, "Ракета", ["korpus"], ["mousemove 578 470", "click 3", "sleep 1.2"])
V_ORDER_BAD = vec(g.landscape_svg(["sonce", "nebo", "hory", "khmara", "trava"]), "Краєвид")
V_ORDER_GOOD = vec(g.landscape_svg(["nebo", "sonce", "khmara", "hory", "trava"]), "Краєвид")
