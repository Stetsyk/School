"""Справжні скриншоти Krita для колод про графіку (6 клас, уроки І-11 … І-15).

Krita запускається під віртуальним дисплеєм (Xvfb) з українським інтерфейсом. Усередині Krita
працює маленький Python-плагін, який виконує сценарій: відкриває малюнок, вмикає інструмент,
додає векторні фігури, виділяє ділянку тощо. Потім зовні xdotool може ще клацнути чи потягнути
мишкою (наприклад, відкрити меню), і знімається весь екран.

Потрібно: krita, krita-l10n (переклад), python3-pyqt5 (скрипти Krita), xvfb, xdotool, imagemagick.
    sudo apt install krita krita-l10n python3-pyqt5 xvfb xdotool imagemagick
Якщо меню лишилося англійським — у системі вимкнено встановлення перекладів (dpkg path-exclude,
так буває в контейнерах). Тоді krita.mo витягують вручну:
    apt-get download krita-l10n && dpkg-deb -x krita-l10n_*.deb /tmp/kl &&
    sudo cp /tmp/kl/usr/share/locale/uk/LC_MESSAGES/krita.mo /usr/share/locale/uk/LC_MESSAGES/

Використання з колоди:
    from kritashot import kshot
    png = kshot([{"open": "/шлях/малюнок.png"}, {"tool": "KisToolBrush"}], xdo=["mousemove 600 400"])

Кроки сценарію (виконуються всередині Krita по черзі):
    {"open": path}                     — відкрити файл (PNG, SVG, KRA…)
    {"new": [w, h, "назва"]}           — новий білий документ
    {"tool": "KisToolBrush"}           — увімкнути інструмент (id дії Krita)
    {"action": "zoom_to_100pct"}       — будь-яка дія Krita за її id; "async": true — якщо вона відкриває діалог
    {"svg": "<svg …>"}                 — додати векторний шар із фігурами
    {"select_shapes": true}            — виділити всі фігури на векторному шарі
    {"select_rect": [x, y, w, h]}      — прямокутне виділення
    {"zoom": 1.5}                      — масштаб перегляду
    {"fg": "#D9342B"}                  — основний колір
    {"brush": "b) Basic-5 Size Opacity"} — набір пензля
    {"paint": [[x, y], …], "size": 30} — провести лінію пензлем (через QPainter на шарі)
    {"layer": "Назва"}                 — новий растровий шар із назвою
    {"png_layer": ["назва", path]}     — растровий шар із готової картинки (розмір як у документа)
    {"hide_docker": "PresetDocker"}   — сховати панель (тоді «Шари» стають на всю висоту)
    {"drop_bg": true}                  — прибрати стандартний шар «Тло»
    {"opacity": ["назва", 50]}         — непрозорість шару, %
    {"hide": "назва"}                  — вимкнути око шару
    {"active": "назва"}                — зробити шар активним
    {"raise_to_top": "назва"}          — перенести шар на верх стопки
    {"wait": 500}                      — пауза, мс
xdo — команди xdotool, які виконуються ззовні вже після сценарію (наприклад, "mousemove 300 200",
"click 1", "key ctrl+z"); можна "sleep 0.5".
"""
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.environ.get("SLIDES_CACHE", os.path.join(tempfile.gettempdir(), "slides-cache"))
SCREEN = (1366, 768)

PLUGIN_DESKTOP = """[Desktop Entry]
Type=Service
ServiceTypes=Krita/PythonPlugin
X-KDE-Library=slideshot
X-Python-2-Compatible=false
Name=slideshot
Comment=Сценарій для скриншотів
"""

PLUGIN_INIT = r'''
import json, os, sys
from krita import Krita, Extension
from PyQt5.QtCore import QTimer, QRect, QPointF
from PyQt5.QtGui import QColor, QImage, QPainter, QPen
from PyQt5.QtWidgets import QApplication

SC = os.environ.get("KSHOT_SCENARIO")
FLAG = os.environ.get("KSHOT_FLAG")
W, H = [int(v) for v in os.environ.get("KSHOT_SCREEN", "1366x768").split("x")]


def log(*a):
    with open(FLAG + ".log", "a") as f:
        print(*a, file=f)


class Shot(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        QTimer.singleShot(2500, self.start)

    def start(self):
        self.steps = json.load(open(SC, encoding="utf-8"))
        self.doc = None
        self.next()

    def win(self):
        return Krita.instance().activeWindow()

    def next(self):
        if not self.steps:
            QTimer.singleShot(1500, self.done)
            return
        st = self.steps.pop(0)
        delay = 400
        try:
            delay = self.do(st) or 400
        except Exception as e:
            log("ERR", st, repr(e))
        QTimer.singleShot(delay, self.next)

    def node(self):
        return self.doc.activeNode()

    def do(self, st):
        k = Krita.instance()
        w = self.win()
        if w is not None:
            qw = w.qwindow()
            if qw.geometry() != QRect(0, 0, W, H):
                qw.setGeometry(0, 0, W, H)
        if "open" in st:
            self.doc = k.openDocument(st["open"])
            w.addView(self.doc)
            return 1500
        if "new" in st:
            ww, hh, name = st["new"][:3]
            self.doc = k.createDocument(ww, hh, name, "RGBA", "U8", "", 72.0)
            # 4-й елемент "transparent" — прозоре тло полотна (як «Непрозорість тла» 0 % у вікні «Створити»)
            self.doc.setBackgroundColor(QColor(0, 0, 0, 0) if st["new"][3:] == ["transparent"] else QColor("white"))
            w.addView(self.doc)
            return 1200
        if "tool" in st:
            a = k.action(st["tool"]) or k.action("KritaShape/" + st["tool"]) or k.action("KritaSelected/" + st["tool"])
            if a is None:
                log("no tool", st["tool"], [x.objectName() for x in k.actions() if "Tool" in x.objectName()])
            else:
                a.trigger()
            return 600
        if "action" in st:
            a = k.action(st["action"])
            if a is None:
                log("no action", st["action"])
            elif st.get("async"):
                QTimer.singleShot(0, a.trigger)   # діалог блокує виклик — запускаємо окремо
            else:
                a.trigger()
            return st.get("delay", 700)
        if "svg" in st:
            layer = self.doc.createVectorLayer(st.get("name", "Векторний шар 1"))
            self.doc.rootNode().addChildNode(layer, None)
            layer.addShapesFromSvg(st["svg"])
            self.doc.setActiveNode(layer)
            return 800
        if "select_shapes" in st:
            for sh in self.node().shapes():
                if st["select_shapes"] is True or sh.name() in st["select_shapes"]:
                    sh.select()
            return 600
        if "select_rect" in st:
            from krita import Selection
            x, y, ww, hh = st["select_rect"]
            sel = Selection()
            sel.select(x, y, ww, hh, 255)
            self.doc.setSelection(sel)
            return 600
        if "zoom" in st:
            c = w.activeView().canvas()
            c.setZoomLevel(st["zoom"])
            return 600
        if "fg" in st:
            from krita import ManagedColor
            col = QColor(st["fg"])
            mc = ManagedColor.fromQColor(col, w.activeView().canvas())
            w.activeView().setForeGroundColor(mc)
            return 300
        if "brush" in st:
            p = k.resources("preset").get(st["brush"])
            if p:
                w.activeView().setCurrentBrushPreset(p)
            else:
                log("no preset", st["brush"])
            return 300
        if "size" in st and "paint" not in st:
            w.activeView().setBrushSize(st["size"])
            return 300
        if "layer" in st:
            layer = self.doc.createNode(st["layer"], "paintlayer")
            self.doc.rootNode().addChildNode(layer, None)
            self.doc.setActiveNode(layer)
            return 500
        if "paint" in st:
            n = self.node()
            ww, hh = self.doc.width(), self.doc.height()
            img = QImage(n.projectionPixelData(0, 0, ww, hh), ww, hh, QImage.Format_ARGB32).copy()
            p = QPainter(img)
            p.setRenderHint(QPainter.Antialiasing)
            pen = QPen(QColor(st.get("color", "#2F3033")))
            pen.setWidthF(st.get("size", 10))
            from PyQt5.QtCore import Qt
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            p.setPen(pen)
            pts = [QPointF(*pt) for pt in st["paint"]]
            for a, b in zip(pts, pts[1:]):
                p.drawLine(a, b)
            p.end()
            ptr = img.constBits()
            ptr.setsize(img.byteCount())
            n.setPixelData(bytes(ptr), 0, 0, ww, hh)
            self.doc.refreshProjection()
            return 500
        if "png_layer" in st:              # новий растровий шар із картинки (PNG того ж розміру, що й документ)
            name, path = st["png_layer"]
            layer = self.doc.createNode(name, "paintlayer")
            self.doc.rootNode().addChildNode(layer, None)
            img = QImage(path).convertToFormat(QImage.Format_ARGB32)
            ptr = img.constBits()
            ptr.setsize(img.byteCount())
            layer.setPixelData(bytes(ptr), 0, 0, img.width(), img.height())
            self.doc.setActiveNode(layer)
            self.doc.refreshProjection()
            return 500
        if "hide_docker" in st:            # сховати панель (напр. PresetDocker — «Набори пензлів»)
            names = st["hide_docker"] if isinstance(st["hide_docker"], list) else [st["hide_docker"]]
            for dw in k.dockers():
                if dw.objectName() in names:
                    dw.hide()
            log("dockers", [dw.objectName() for dw in k.dockers() if dw.isVisible()])
            return 600
        if "drop_bg" in st:                # прибрати стандартний шар «Тло»
            kids = self.doc.rootNode().childNodes()
            if kids:
                kids[0].remove()
            self.doc.refreshProjection()
            return 400
        if "opacity" in st:                # [назва шару, 0…100 %]
            n = self.doc.nodeByName(st["opacity"][0])
            n.setOpacity(int(round(st["opacity"][1] * 255 / 100)))
            self.doc.refreshProjection()
            return 400
        if "hide" in st:
            self.doc.nodeByName(st["hide"]).setVisible(False)
            self.doc.refreshProjection()
            return 400
        if "active" in st:
            self.doc.setActiveNode(self.doc.nodeByName(st["active"]))
            return 500
        if "raise_to_top" in st:           # перенести шар на самий верх стопки
            n = self.doc.nodeByName(st["raise_to_top"])
            root = self.doc.rootNode()
            kids = root.childNodes()
            n2 = n.duplicate()
            n2.setName(n.name())
            root.addChildNode(n2, kids[-1])
            n.remove()
            self.doc.setActiveNode(n2)
            self.doc.refreshProjection()
            return 600
        if "wait" in st:
            return st["wait"]
        log("unknown step", st)
        return 100

    def done(self):
        open(FLAG, "w").write("ok")
        QTimer.singleShot(300, self.poll)

    def poll(self):
        """Після xdo ззовні можуть попросити зберегти документ: файл FLAG.more зі списком кроків."""
        more = FLAG + ".more"
        if os.path.exists(more):
            steps = json.load(open(more, encoding="utf-8"))
            os.remove(more)
            for st in steps:
                try:
                    self.save(st)
                except Exception as e:
                    log("ERR", st, repr(e))
            open(FLAG + ".more.ok", "w").write("ok")
        QTimer.singleShot(300, self.poll)

    def save(self, st):
        from krita import InfoObject
        doc = Krita.instance().activeDocument() or self.doc
        doc.waitForDone()
        if "save_kra" in st:
            doc.setBatchmode(True)
            ok = doc.saveAs(st["save_kra"])
            doc.waitForDone()
            log("save_kra", st["save_kra"], ok)
        if "export_png" in st:
            doc.setBatchmode(True)
            info = InfoObject()
            info.setProperty("alpha", True)
            info.setProperty("compression", 6)
            ok = doc.exportImage(st["export_png"], info)
            doc.waitForDone()
            log("export_png", st["export_png"], ok)


Krita.instance().addExtension(Shot(Krita.instance()))
'''


def _env(home, scen, flag, scale=1):
    cfg = os.path.join(home, ".config")
    data = os.path.join(home, ".local", "share")
    plug = os.path.join(data, "krita", "pykrita")
    os.makedirs(os.path.join(plug, "slideshot"), exist_ok=True)
    os.makedirs(cfg, exist_ok=True)
    open(os.path.join(plug, "slideshot.desktop"), "w").write(PLUGIN_DESKTOP)
    open(os.path.join(plug, "slideshot", "__init__.py"), "w").write(PLUGIN_INIT)
    open(os.path.join(cfg, "kritarc"), "w").write(
        "[python]\nenable_slideshot=true\n\n[General]\nshowSplashScreen=false\nhideSplashAfterStartup=true\n")
    open(os.path.join(cfg, "klanguageoverridesrc"), "w").write("[Language]\nkrita=uk\n")
    env = dict(os.environ)
    env.update({"HOME": home, "XDG_CONFIG_HOME": cfg, "XDG_DATA_HOME": data, "LANG": "uk_UA.UTF-8",
                "LANGUAGE": "uk", "LC_ALL": "uk_UA.UTF-8", "QT_QPA_PLATFORM": "xcb",
                "KSHOT_SCENARIO": scen, "KSHOT_FLAG": flag, "KSHOT_SCREEN": f"{SCREEN[0]}x{SCREEN[1]}"})
    if scale != 1:  # чіткі скріни: інтерфейс удвічі більшими пікселями, а координати лишаються ті самі
        env.update({"QT_SCALE_FACTOR": str(scale), "QT_AUTO_SCREEN_SCALE_FACTOR": "0"})
    return env


def _scale_cmd(cmd, k):
    """xdotool працює у фізичних пікселях: при scale=2 координати mousemove множимо."""
    p = cmd.split()
    if k != 1 and p and p[0] == "mousemove":
        p = [p[0]] + [str(int(round(float(v) * k))) if v.lstrip("-").replace(".", "").isdigit() else v for v in p[1:]]
    return p


def kshot(scenario, xdo=None, crop=None, screen=None, scale=1, save=None):
    """Повертає шлях до PNG зі скриншотом усього вікна Krita. crop=(x, y, w, h) — вирізати частину.
    scale=2 — чіткий скрін (Retina): екран 1366 × 768 точок знімається як 2732 × 1536 пікселів; координати в
    сценарії, xdo і crop — у точках, як і при scale=1.
    save=[{"save_kra": шлях}, {"export_png": шлях}] — після xdo справжня Krita зберігає документ (додатки-зразки)."""
    global SCREEN
    SCREEN = tuple(screen or SCREEN)
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.md5(json.dumps([scenario, xdo, crop, SCREEN, PLUGIN_INIT, scale, save], ensure_ascii=False).encode()
                      + b"".join(open(st["open"], "rb").read() for st in scenario if "open" in st)).hexdigest()[:16]
    png = os.path.join(CACHE, "krita-" + key + ".png")
    if os.path.exists(png) and not save:
        return png
    home = tempfile.mkdtemp(prefix="kshot-")
    scen = os.path.join(home, "scenario.json")
    flag = os.path.join(home, "ready")
    json.dump(scenario, open(scen, "w", encoding="utf-8"), ensure_ascii=False)
    env = _env(home, scen, flag, scale)
    disp = ":%d" % (60 + int(key[:4], 16) % 200)
    xv = subprocess.Popen(["Xvfb", disp, "-screen", "0", f"{SCREEN[0] * scale}x{SCREEN[1] * scale}x24", "-nolisten", "tcp"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    env["DISPLAY"] = disp
    time.sleep(1.5)
    kr = subprocess.Popen(["krita", "--nosplash"], env=env, stdout=open(os.path.join(home, "krita.out"), "w"),
                          stderr=subprocess.STDOUT)
    try:
        t0 = time.time()
        while not os.path.exists(flag):
            if time.time() - t0 > 150 or kr.poll() is not None:
                raise RuntimeError("Krita не дійшла до кінця сценарію:\n" +
                                   (open(flag + ".log").read() if os.path.exists(flag + ".log") else "") +
                                   open(os.path.join(home, "krita.out")).read()[-1500:])
            time.sleep(0.5)
        for cmd in (xdo or []):
            if cmd.startswith("sleep"):
                time.sleep(float(cmd.split()[1]))
            else:
                subprocess.run(["xdotool"] + _scale_cmd(cmd, scale), env=env, check=False)
                time.sleep(0.4)
        time.sleep(1.0)
        if save:
            json.dump(save, open(flag + ".more", "w", encoding="utf-8"), ensure_ascii=False)
            t0 = time.time()
            while not os.path.exists(flag + ".more.ok"):
                if time.time() - t0 > 90:
                    raise RuntimeError("Krita не зберегла файл: " + open(flag + ".log").read()[-800:])
                time.sleep(0.5)
        raw = os.path.join(home, "raw.png")
        subprocess.run(["import", "-window", "root", raw], env=env, check=True)
        if crop:
            x, y, w, h = [v * scale for v in crop]
            subprocess.run(["convert", raw, "-crop", f"{w}x{h}+{x}+{y}", "+repage", png], check=True)
        else:
            shutil.copy(raw, png)
        if os.path.exists(flag + ".log"):
            print(open(flag + ".log").read())
    finally:
        kr.kill()
        xv.kill()
        shutil.rmtree(home, ignore_errors=True)
    return png


if __name__ == "__main__":
    import sys
    sc = json.load(open(sys.argv[1], encoding="utf-8"))
    print(kshot(sc.get("steps", []), sc.get("xdo")))
