"""Справжні скриншоти Blender з українським інтерфейсом (для колод 9 класу «3D-графіка»).

Як працює: Xvfb 2732 × 1536 (+GLX, програмний OpenGL Mesa) → Blender 4 з `--factory-startup` і скриптом:
інтерфейс українською, масштаб інтерфейсу 2 (тобто екран 1366 × 768 «точок» у подвійній чіткості, як Retina),
потім виконується код сцени (setup) — будуємо об’єкти через Python API, вибираємо, міняємо режим, перегляд тощо.
Коли сцена готова, ззовні йдуть дії мишки й клавіш xdotool (координати в точках) і знімок усього екрана.

    from blendershot import bshot
    png = bshot('''
    bpy.ops.mesh.primitive_uv_sphere_add(location=(2, 0, 1))
    ''', xdo=["mousemove 280 40", "click 1"])           # відкрили меню «Додати»

Потрібно: blender (4.x), xvfb, xdotool, imagemagick; український переклад
/usr/share/locale/uk/LC_MESSAGES/blender.mo (у Debian/Ubuntu його можна витягти з пакета blender-data:
`apt-get download blender-data && dpkg-deb -x blender-data_*.deb x`, бо локалі часто вирізані з образу).

bmake(setup, blend=..., png=..., anim=...) — те саме без вікна: будує сцену, зберігає .blend і рендерить PNG
(Cycles на процесорі — без відеокарти) або кадри анімації → GIF/MP4 (ffmpeg). Це «Додатки» — готові зразки."""
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
SCALE = 2

PRELUDE = r'''
import bpy, math, os, sys
from mathutils import Vector, Euler
P = bpy.context.preferences
P.view.language = "uk_UA"
P.view.use_translate_interface = True
P.view.use_translate_tooltips = True
P.view.use_translate_new_dataname = True     # нові об’єкти — «Куб», «Сфера», як в учнів
P.view.ui_scale = float(os.environ.get("BSHOT_SCALE", "1"))
P.view.show_splash = False
P.view.show_tooltips = False

def area(kind="VIEW_3D"):
    for a in bpy.context.screen.areas:
        if a.type == kind:
            return a

def view3d():
    return area().spaces.active

def region3d():
    return view3d().region_3d

def view(rot=(60, 0, 45), dist=12, target=(0, 0, 0.6), persp=True):
    """Кут огляду: rot — нахил і поворот у градусах, dist — відстань."""
    r = region3d()
    r.view_rotation = Euler([math.radians(v) for v in rot], "XYZ").to_quaternion()
    r.view_distance = dist
    r.view_location = Vector(target)
    r.view_perspective = "PERSP" if persp else "ORTHO"

def shading(kind="SOLID"):
    view3d().shading.type = kind

def clean(cam=(13, -13, 9), target=(0, 0, 1)):
    """Порожня сцена без куба. Камеру й світло лишаємо (як у стартовому файлі), але відсуваємо камеру далі, щоб
    вона не заступала моделі на скрінах, і повертаємо її на target."""
    for o in list(bpy.data.objects):
        if o.type == "MESH":
            bpy.data.objects.remove(o, do_unlink=True)
    look(bpy.data.objects.get("Camera"), cam, target)
    lt = bpy.data.objects.get("Light")
    if lt:
        lt.location = (6, -4, 9)
        lt.data.energy = 1500

def look(obj, loc, target=(0, 0, 0)):
    if obj is None:
        return
    obj.location = loc
    d = Vector(target) - Vector(loc)
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

def ground(size=20, color="#C9CED6", name="Підлога"):
    return add("plane", name, loc=(0, 0, 0), scale=(size / 2, size / 2, 1), color=color)

def world(color=(0.78, 0.84, 0.92), strength=1.0):
    w = bpy.context.scene.world
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (*color, 1)
    bg.inputs[1].default_value = strength

def sun(energy=3.5, rot=(50, 10, 30)):
    bpy.ops.object.light_add(type="SUN", rotation=[math.radians(v) for v in rot])
    o = bpy.context.active_object
    o.name = "Сонце"
    o.data.energy = energy
    return o

def select(*names):
    bpy.ops.object.select_all(action="DESELECT")
    for n in names:
        o = bpy.data.objects[n]
        o.select_set(True)
        bpy.context.view_layer.objects.active = o

def mat(obj, color, name=None, metal=0.0, rough=0.5, alpha=1.0, emit=0.0):
    m = bpy.data.materials.new(name or ("Матеріал " + obj.name))
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        m.blend_method = "BLEND"
    if emit:
        b.inputs["Emission Color"].default_value = (*color, 1)
        b.inputs["Emission Strength"].default_value = emit
    m.diffuse_color = (*color, alpha)
    obj.data.materials.clear()
    obj.data.materials.append(m)
    return m

def hexc(h):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)

def add(kind, name, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), color=None, **kw):
    """Примітив: cube, uv_sphere, cylinder, cone, torus, plane, ico_sphere, monkey."""
    getattr(bpy.ops.mesh, "primitive_" + kind + "_add")(location=loc, rotation=[math.radians(v) for v in rot], **kw)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    if color:
        mat(o, hexc(color))
    return o

def props_tab(ctx="OBJECT"):
    a = area("PROPERTIES")
    if a:
        a.spaces.active.context = ctx

def outliner_expand():
    pass
'''

GUI_TAIL = r'''
def _ready():
    try:
        open(os.environ["BSHOT_FLAG"], "w").write("ok")
    except Exception as e:
        print("FLAG ERR", e)
    return None

def _run():
    try:
        with bpy.context.temp_override(window=bpy.context.window_manager.windows[0],
                                       area=area(), screen=bpy.context.window_manager.windows[0].screen):
            exec(compile(open(os.environ["BSHOT_SETUP"], encoding="utf-8").read(), "setup", "exec"), globals())
    except Exception as e:
        import traceback
        traceback.print_exc()
        open(os.environ["BSHOT_FLAG"] + ".err", "w").write(traceback.format_exc())
    bpy.app.timers.register(_ready, first_interval=2.0)
    return None

bpy.app.timers.register(_run, first_interval=3.0)
'''


def _scale_cmd(cmd, k):
    p = cmd.split()
    if p and p[0] in ("mousemove", "mousedown_at"):
        p = [p[0]] + [str(int(round(float(v) * k))) if v.lstrip("-").replace(".", "").isdigit() else v for v in p[1:]]
    return p


def bshot(setup, xdo=None, scale=SCALE, wait=1.5):
    """Скриншот усього вікна Blender (PNG 2732 × 1536 при scale=2). setup — Python-код сцени (bpy і допоміжні
    функції з PRELUDE: add, view, shading, select, mat, clean, props_tab). xdo — дії xdotool у точках екрана."""
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.md5(json.dumps([setup, xdo, scale, PRELUDE, GUI_TAIL, SCREEN], ensure_ascii=False).encode()).hexdigest()[:16]
    png = os.path.join(CACHE, "blender-" + key + ".png")
    if os.path.exists(png):
        return png
    home = tempfile.mkdtemp(prefix="bshot-")
    script = os.path.join(home, "run.py")
    open(script, "w", encoding="utf-8").write(PRELUDE + GUI_TAIL)
    st = os.path.join(home, "setup.py")
    open(st, "w", encoding="utf-8").write(setup)
    flag = os.path.join(home, "ready")
    env = dict(os.environ)
    env.update({"HOME": home, "BSHOT_FLAG": flag, "BSHOT_SETUP": st, "BSHOT_SCALE": str(scale),
                "LIBGL_ALWAYS_SOFTWARE": "1", "LANG": "uk_UA.UTF-8"})
    disp = ":%d" % (300 + int(key[:4], 16) % 300)
    xv = subprocess.Popen(["Xvfb", disp, "-screen", "0", f"{SCREEN[0] * scale}x{SCREEN[1] * scale}x24", "+extension",
                           "GLX", "-nolisten", "tcp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    env["DISPLAY"] = disp
    time.sleep(1.5)
    log = open(os.path.join(home, "blender.out"), "w")
    bl = subprocess.Popen(["blender", "--factory-startup", "-noaudio", "--window-geometry", "0", "0",
                           str(SCREEN[0] * scale), str(SCREEN[1] * scale), "--python", script],
                          env=env, stdout=log, stderr=subprocess.STDOUT)
    try:
        t0 = time.time()
        while not os.path.exists(flag):
            if time.time() - t0 > 150 or bl.poll() is not None:
                raise RuntimeError("Blender не дійшов до кінця сценарію:\n" + open(log.name).read()[-2500:])
            time.sleep(0.5)
        if os.path.exists(flag + ".err"):
            raise RuntimeError("Помилка в setup:\n" + open(flag + ".err").read())
        time.sleep(wait)
        for cmd in (xdo or []):
            if cmd.startswith("sleep"):
                time.sleep(float(cmd.split()[1]))
            else:
                subprocess.run(["xdotool"] + _scale_cmd(cmd, scale), env=env, check=False)
                time.sleep(0.5)
        time.sleep(1.2)
        raw = os.path.join(home, "raw.png")
        subprocess.run(["import", "-window", "root", raw], env=env, check=True)
        shutil.copy(raw, png)
    finally:
        bl.kill()
        xv.kill()
        shutil.rmtree(home, ignore_errors=True)
    return png


BG_TAIL = r'''
import traceback
try:
    exec(compile(open(os.environ["BSHOT_SETUP"], encoding="utf-8").read(), "setup", "exec"), globals())
    out = json.loads(os.environ["BSHOT_OUT"])
    sc = bpy.context.scene
    if out.get("blend"):
        bpy.ops.wm.save_as_mainfile(filepath=out["blend"], compress=True)
    if out.get("png") or out.get("frames"):
        sc.render.engine = out.get("engine", "CYCLES")
        if sc.render.engine == "CYCLES":
            sc.cycles.device = "CPU"
            sc.cycles.samples = out.get("samples", 48)
            sc.cycles.use_denoising = False
        sc.render.resolution_x, sc.render.resolution_y = out.get("res", (1280, 720))
        sc.render.resolution_percentage = 100
        sc.render.film_transparent = False
    if out.get("png"):
        sc.render.image_settings.file_format = "PNG"
        sc.render.filepath = out["png"]
        bpy.ops.render.render(write_still=True)
    if out.get("frames"):
        sc.render.image_settings.file_format = "PNG"
        sc.render.filepath = out["frames"] + "/f_"
        bpy.ops.render.render(animation=True)
except Exception:
    traceback.print_exc()
    open(os.environ["BSHOT_OUT"] and json.loads(os.environ["BSHOT_OUT"])["err"], "w").write(traceback.format_exc())
'''


def bmake(setup, blend=None, png=None, anim=None, engine="CYCLES", samples=48, res=(1280, 720), fps=24):
    """Без вікна: будує сцену setup, зберігає .blend (blend), рендерить PNG (png) або анімацію anim (шлях .gif/.mp4;
    кадри — з налаштувань сцени frame_start…frame_end). Сам Blender, справжні файли."""
    home = tempfile.mkdtemp(prefix="bmake-")
    st = os.path.join(home, "setup.py")
    open(st, "w", encoding="utf-8").write(setup)
    script = os.path.join(home, "run.py")
    open(script, "w", encoding="utf-8").write(PRELUDE.replace('P.view.ui_scale', '# P.view.ui_scale')
                                               + "\nimport json\n" + BG_TAIL)
    frames = os.path.join(home, "frames") if anim else None
    if frames:
        os.makedirs(frames)
    err = os.path.join(home, "err.txt")
    out = {"blend": blend, "png": png, "frames": frames, "engine": engine, "samples": samples, "res": list(res),
           "err": err}
    env = dict(os.environ)
    env.update({"HOME": home, "BSHOT_SETUP": st, "BSHOT_OUT": json.dumps(out, ensure_ascii=False),
                "LIBGL_ALWAYS_SOFTWARE": "1", "LANG": "uk_UA.UTF-8"})
    for p in (blend, png, anim):
        if p:
            os.makedirs(os.path.dirname(p), exist_ok=True)
    cmd = ["blender", "--factory-startup", "-noaudio", "-b", "--python", script]
    if engine != "CYCLES":   # Eevee й Workbench потребують OpenGL — даємо віртуальний дисплей
        cmd = ["xvfb-run", "-a", "-s", "-screen 0 1280x720x24 +extension GLX"] + cmd
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=3600)
    if os.path.exists(err):
        raise RuntimeError(open(err).read() + r.stdout[-1500:])
    if anim:
        if anim.endswith(".gif"):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{frames}/f_%04d.png",
                            "-vf", "fps=12,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse",
                            anim], check=True)
        else:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{frames}/f_%04d.png",
                            "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", anim], check=True)
    shutil.rmtree(home, ignore_errors=True)
    return blend, png, anim
