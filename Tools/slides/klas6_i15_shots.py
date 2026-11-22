"""Справжні скріни Krita для колоди 6 клас, урок І-15 «Текст у зображеннях. Підсумок» (імпортується з klas6_i15.py).
Плакат до змагань (shary6.py): фон, м’яч, деталі — растрові шари; підкладка, заголовок, дата — векторні.
Текст набирає справжній інструмент «Текст» Krita у вікні «Текстовий редактор»."""
import shary6 as h
from kritakroky import kk, box, row_box, TOOL, LAYERS, AWAY

ZP = 0.42                                   # плакат 2000 × 1400 у кадрі «полотно + шари»
ROW = [h.doc_rect(ZP, h.PW, h.PH), (1100, 336, 1366, 622)]
ZT = 0.5                                    # плакат під час набору тексту
DT = h.doc_rect(ZT, h.PW, h.PH)

# інструмент «Текст»: протягнули рамку вгорі полотна → вікно «Текстовий редактор» → набрали «Змагання», розмір 72
TEXT_START = h.poster_steps(zoom=ZT, active="деталі", upto="деталі") + [{"tool": "SvgTextTool"}]
x0, y0 = DT[0] + 80, DT[1] + 50
DRAG = [f"mousemove {x0} {y0}", "mousedown 1", f"mousemove {x0 + 150} {y0 + 30}", f"mousemove {x0 + 300} {y0 + 60}",
        "mouseup 1", "sleep 2.5"]
TYPE = ["mousemove 600 420", "click 1", "key ctrl+a", "type --delay 250 Змагання", "sleep 0.5", "key ctrl+a",
        "mousemove 1030 209", "click 1", "key ctrl+a", "type 120", "key Return", "sleep 0.8",
        "mousemove 600 420", "click 1", "key ctrl+End", "sleep 0.5", "mousemove 1300 700"]
TEXT_DIALOG = kk(TEXT_START, DRAG + TYPE, layout="row",
                 parts=[(0, 70, 62, 100), (228, 190, 1135, 490), (930, 600, 1132, 636)],
                 marks=[box(TOOL["Текст"], "bottom"), (250, 318, 1040, 480, "left"), (232, 195, 1100, 223, "top"),
                        (945, 605, 1030, 632, "left")],
                 nums=(1, 3, 4, 5))
TEXT_DONE = kk(TEXT_START, DRAG + TYPE + ["mousemove 989 612", "click 1", "sleep 1.5", "mousemove 1085 612", "click 1",
                                          "sleep 2", "key Escape", "sleep 1", "mousemove 1300 760"],
               parts=[DT, (1100, 336, 1366, 622)], layout="row",
               marks=[(DT[0] + 72, DT[1] + 24, DT[0] + 230, DT[1] + 64, "right"), row_box(0, "row", "right")])

# підкладка: шар «підкладка» між деталями й заголовком, непрозорість
PODKLADKA = kk(h.poster_steps(zoom=ZP, active="підкладка"), [AWAY], parts=ROW, layout="row",
               marks=[row_box(2, "row", "right"), box(LAYERS["Непрозорість"], "right")])
# порядок збирання: фон → головний → деталі → текст (нумерація знизу вгору)
ORDER = kk(h.poster_steps(zoom=ZP, active="дата"), [AWAY], parts=ROW, layout="row",
           marks=[row_box(5, "row", "right"), row_box(4, "row", "right"), row_box(3, "row", "right"),
                  (1104, 427, 1362, 507, "right")])
POSTER = kk(h.poster_steps(zoom=0.55, active="дата"), [AWAY], parts=[h.doc_rect(0.55, h.PW, h.PH)])

if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.isupper() and isinstance(v, str) and v.endswith(".png"):
            print(k, v)
